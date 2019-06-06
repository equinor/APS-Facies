import Vue from 'vue'
import { cloneDeep } from 'lodash'

import templates from '@/store/templates/truncationRules'
import simpleTemplates from '@/store/templates/simpleTruncationRules'
import types from '@/store/modules/truncationRules/types'
import { addItem } from '@/store/actions'
import { ADD_ITEM } from '@/store/mutations'
import { isUUID } from '@/utils/helpers'
import {
  combinePolygons,
  getFaciesGroup,
  makePolygonsFromSpecification,
  makeRule,
  processFields,
  processOverlay,
  processPolygons,
  structurePolygons,
} from '@/utils/helpers/processing/templates'
import { isEmpty } from '@/utils'
import { Orientation } from '@/utils/domain/truncationRule/cubic'
import { CubicPolygon, OverlayPolygon } from '@/utils/domain'
import APSError from '@/utils/domain/errors/base'

const missingTemplates = (_templates, state) => {
  const name = template => {
    const type = isUUID(template.type)
      ? state.types.available[template.type].type
      : template.type
    return `${type}::${template.name}`
  }
  const names = Object.values(_templates).map(template => name(template))
  return templates.templates.filter((template) => names.indexOf(name(template)) === -1)
}

const addProportions = (polygons) => {
  const proportions = []
  if (isEmpty(polygons)) return proportions
  Object.values(polygons).forEach(({ facies, proportion }) => {
    proportions.push({ facies, probability: proportion || 1 })
  })
  return proportions
}

const normalize = (items) => {
  const sum = items.reduce((sum, { probability }) => sum + probability, 0)
  return items.map(payload => { return { ...payload, probability: payload.probability / sum } })
}

function organizeCubicPolygons (polygons, levels) {
  const allPolygons = []
  if (polygons.length === 0) return polygons
  const root = new CubicPolygon({ order: -1 })
  for (let i = 0; i < levels.length; i++) {
    const polygon = polygons[`${i}`]
    if (polygon instanceof OverlayPolygon) {
      allPolygons.push(polygon)
    } else {
      const levelSpecification = levels[`${i}`]
      let current = root
      for (let j = 0; j < levelSpecification.length; j++) {
        const level = levelSpecification[`${j}`]
        if (level <= 0) continue
        let polygon = current.children.find(polygon => polygon.order === level)
        if (!polygon) {
          if (j + 1 < levelSpecification.length && levelSpecification[`${j + 1}`] > 0) {
            polygon = new CubicPolygon({ parent: current, order: level })
          } else {
            polygon = polygons[`${i}`]
            polygon.order = level
            current.add(polygon)
          }
        }
        current = polygon
      }
    }
  }
  const queue = [root]
  while (queue.length > 0) {
    const current = queue.shift()
    allPolygons.push(current)
    current.children.forEach(polygon => {
      queue.push(polygon)
    })
  }
  return allPolygons
}

function getDirection (settings) {
  const mapping = {
    'H': Orientation.HORIZONTAL,
    'V': Orientation.VERTICAL,
  }
  let direction = settings[0].direction
  if (typeof direction !== 'string') return null
  direction = mapping[direction.toUpperCase()]
  return !Object.is(direction, undefined)
    ? direction
    : null
}

export default {
  namespaced: true,

  state: {
    available: {},
  },

  modules: {
    types,
  },

  actions: {
    fetch ({ dispatch }) {
      return Promise.all([
        dispatch('types/fetch'),
        ...templates.templates.map(template => dispatch('add', template)),
        ...simpleTemplates.templates.map(template => dispatch('add', template))
      ])
    },
    async populate ({ commit, dispatch, state }, { available, types }) {
      await dispatch('types/populate', types.available)
      // TODO: Deal with there being other 'official' templates than those to be populated
      commit('AVAILABLE', available)
      const missing = missingTemplates(available, state)
      return Promise.all(missing.map(template => dispatch('add', template)))
    },
    add ({ commit, state }, template) {
      template = cloneDeep(template)
      template.type = Object.keys(state.types.available).find(id => state.types.available[`${id}`].type === template.type)
      return addItem({ commit }, { item: template })
    },
    async createRule ({ dispatch, state, rootGetters, rootState }, { name, type, parent = null }) {
      const autoFill = rootState.options.automaticFaciesFill.value

      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }

      const template = Object.values(state.available).find(template => template.name === name && template.type === type)
      type = state.types.available[`${type}`].type
      const missing = template.minFields - Object.values(rootGetters.fields).length
      if (missing > 0) {
        for (const _ of [...Array(missing)]) {
          await dispatch('gaussianRandomFields/addEmptyField', {}, { root: true })
        }
      }
      if (autoFill && template.overlay) {
        await Promise.all(template.overlay.items.map(item => getFaciesGroup({ rootGetters, dispatch }, item.over, parent)))
      }
      const backgroundFields = processFields(rootGetters, rootState, template.fields, parent)
      const overlay = processOverlay(rootGetters, template.overlay, parent)
      let polygons = processPolygons({ rootGetters, rootState }, { type, polygons: template.polygons, settings: template.settings })
      polygons = combinePolygons(polygons, overlay)
      polygons = structurePolygons(polygons)
      const levels = polygons.map(({ level }) => level)
      polygons = makePolygonsFromSpecification(polygons)
      if (type === 'cubic') {
        polygons = organizeCubicPolygons(polygons, levels)
      }

      const uniqueFacies = [...polygons
        .reduce((facies, polygon) => {
          if (polygon.facies) {
            facies.add(polygon.facies)
          }
          return facies
        }, new Set())]
      await Promise.all(uniqueFacies.map(async facies => {
        if (facies) {
          await dispatch('facies/updateProbability', { facies, probability: 1 / uniqueFacies.length }, { root: true })
        } else {
          throw new APSError(`The facies ${facies} does not exist`)
        }
      }))
      if (uniqueFacies.length === 0) {
        // This is a simple template, without any facies specification
        // However, at least two facies HAS to be selected in order to create a truncation rule
        await dispatch('facies/normalize', undefined, { root: true })
      }
      const direction = getDirection(template.settings)

      const rule = makeRule({
        type,
        direction,
        polygons,
        backgroundFields,
        overlay,
        name,
        ...parent,
      })
      await dispatch('truncationRules/add', rule, { root: true })

      if (autoFill) {
        if (rootGetters['facies/unset']) {
          const proportions = addProportions(rule.polygons)
          await Promise.all(normalize(proportions)
            .map(payload => dispatch('facies/updateProbability', payload, { root: true }))
          )
        }
      }
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.available, { id, item })
    },
    AVAILABLE: (state, templates) => {
      Vue.set(state, 'available', templates)
    },
  },
}
