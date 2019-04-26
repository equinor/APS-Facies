import Vue from 'vue'
import { cloneDeep } from 'lodash'

import templates from '@/store/templates/truncationRules'
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

const missingTemplates = (_templates, state) => {
  const name = template => {
    const type = isUUID(template.type) ? state.types.available[template.type].type : template.type
    return `${type}::${template.name}`
  }
  const names = Object.values(_templates).map(template => name(template))
  return templates.templates.filter((template) => names.indexOf(name(template)) === -1)
}

const addProportions = (proportions, polygons) => {
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
      let polygons = processPolygons({ rootGetters, rootState }, { type, polygons: template.polygons, settings: template.settings })
      const backgroundFields = processFields(rootGetters, rootState, template.fields, template.parent)
      const overlay = processOverlay(rootGetters, template.overlay, parent)
      polygons = combinePolygons(polygons, overlay)
      polygons = structurePolygons(polygons)
      polygons = makePolygonsFromSpecification(polygons)

      const uniqueFacies = [...polygons
        .reduce((facies, polygon) => {
          facies.add(polygon.facies)
          return facies
        }, new Set())]
      await Promise.all(uniqueFacies.map(async facies => {
        if (facies) {
          await dispatch('facies/updateProbability', { facies, probability: 1 / uniqueFacies.length }, { root: true })
        } else {
          // TODO: Handle appropriately
          // throw new Error(`The facies ${polygon.facies} does not exist`)
        }
      }))

      const rule = makeRule({
        type,
        polygons,
        backgroundFields,
        overlay,
        name,
        ...parent,
      })
      await dispatch('truncationRules/add', rule, { root: true })

      if (autoFill) {
        if (rootGetters['facies/unset']) {
          const proportions = []
          addProportions(proportions, rule.polygons)
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
