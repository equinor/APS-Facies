import Vue from 'vue'
import { cloneDeep, isNumber } from 'lodash'

import api from '@/api/rms'

import templates from '@/store/modules/truncationRules/templates'

import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import {
  hasCurrentParents,
  minFacies,
  hasEnoughFacies,
  isEmpty,
  makeTruncationRuleSpecification,
  notEmpty,
} from '@/utils'
import { getId } from '@/utils/helpers'
import { makeRule } from '@/utils/helpers/processing/templates'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import APSTypeError from '@/utils/domain/errors/type'
import APSError from '@/utils/domain/errors/base'
import { makePolygonsFromSpecification } from '@/utils/helpers/processing/templates/typed'

const changePreset = (state, thing, item) => {
  Vue.set(state.preset, thing, item)
}

const findPolygonInRule = (rule, polygon) => {
  return rule._polygons[`${polygon.id}`]
}

const setFacies = (polygons, src, dest) => {
  polygons[`${dest.id}`].facies = src.facies
}

function swapFacies (rule, polygons) {
  if (polygons.length !== 2) throw new Error('Only two polygons may be swapped')
  const newPolygons = cloneDeep(rule._polygons)

  const first = findPolygonInRule(rule, polygons[0])
  const other = findPolygonInRule(rule, polygons[1])

  setFacies(newPolygons, first, other)
  setFacies(newPolygons, other, first)

  return newPolygons
}

const setPolygonValue = (state, rule, polygon, property, value) => {
  Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], property, value)
}

const setProperty = (state, rule, property, values) => {
  Vue.set(state.rules[`${rule.id}`], property, values)
}

function compareTemplate (rootGetters, a, b) {
  const _minFacies = item => minFacies(item, rootGetters)
  if (_minFacies(a) > _minFacies(b)) {
    return +1
  } else if (_minFacies(a) < _minFacies(b)) {
    return -1
  } else {
    return a.name.localeCompare(b.name)
  }
}

function increaseOrderByRelativeTo ({ commit }, rule, polygon, amount = 1) {
  rule.polygons.forEach(_polygon => {
    if (_polygon.order >= polygon.order && _polygon.overlay === polygon.overlay) {
      commit('CHANGE_ORDER', { rule, polygon: _polygon, order: _polygon.order + amount })
    }
  })
}

export default {
  namespaced: true,

  state: {
    rules: {},
    preset: {
      type: '',
      template: '',
    },
  },

  modules: {
    templates,
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('templates/fetch')
    },
    async add ({ commit }, rule) {
      return addItem({ commit }, { item: rule })
    },
    remove ({ commit, state, rootGetters }, ruleId) {
      const correctId = _id => isEmpty(_id) || !state.rules.hasOwnProperty(_id)

      if (correctId(ruleId)) {
        ruleId = rootGetters.truncationRule.id
      }

      if (correctId(ruleId)) {
        commit('REMOVE', ruleId)
      } else {
        throw new Error(`The rule with ID ${ruleId} does not exist. Cannot be removed`)
      }
    },
    async populate ({ commit, dispatch, rootGetters }, { rules, templates, preset }) {
      if (preset.type) commit('CHANGE_TYPE', preset)
      if (preset.template) commit('CHANGE_TEMPLATE', preset)
      await dispatch('templates/populate', templates)
      Object.values(rules).forEach(rule => {
        rule.backgroundFields = rule.backgroundFields.map(({ id }) => rootGetters['gaussianRandomFields/byId'](id))
        rule.polygons.forEach(polygon => {
          polygon.facies = rootGetters['facies/byId'](polygon.facies.id)
          if (polygon.overlay) {
            polygon.field = rootGetters['gaussianRandomFields/byId'](polygon.field.id)
            polygon.group = rootGetters['facies/groups/byId'](polygon.group.id)
          }
        })
        rule.polygons = makePolygonsFromSpecification(rule.polygons)
        commit('ADD', { id: rule.id, item: makeRule(rule) })
      })
    },
    async addPolygon ({ commit, dispatch, rootState }, { rule, group = '', order = null, overlay = false }) {
      if (rule.type === 'bayfill') throw new Error('Bayfill must have exactly 5 polygons. Cannot add more.')

      if (!isNumber(order) || order < 0) {
        const polygons = rule.polygons
        // TODO: Filter on group as well
          .filter(polygon => polygon.overlay === overlay)
        order = polygons.length === 0
          ? 0
          : 1 + polygons
            .map(polygon => polygon.order)
            .reduce((max, curr) => curr > max ? curr : max, 0)
      }
      let polygon = null
      if (overlay) {
        let field = null
        if (
          (
            rule.overlayPolygons
              .filter(polygon => getId(polygon.group) === getId(group)).length + 1
          ) > (Object.values(rootState.gaussianRandomFields.fields).length - rule.backgroundFields.length)
        ) {
          field = await dispatch('gaussianRandomFields/addEmptyField', { ...rule.parent }, { root: true })
        }
        polygon = new OverlayPolygon({ group, field, order })
      } else if (rule.type === 'non-cubic') {
        polygon = new NonCubicPolygon({ order })
      } else if (rule.type === 'cubic') {
        throw new Error('Cubic is not implemented')
      } else {
        throw new APSTypeError('Invalid type')
      }
      increaseOrderByRelativeTo({ commit }, rule, polygon)
      commit('ADD_POLYGON', { rule, polygon })
    },
    async removePolygon ({ commit, dispatch, rootState }, { rule, polygon }) {
      // TODO: Decrease orders
      commit('REMOVE_POLYGON', { rule, polygon })
      // Decrease the order of polygons
      increaseOrderByRelativeTo({ commit }, rule, polygon, -1)

      // Remove from facies group (if it is no longer a background facies)
      if (!rule.backgroundPolygons.map(({ facies }) => facies.id).includes(polygon.facies.id)) {
        const group = Object.values(rootState.facies.groups.available).find(group => group.has(polygon.facies))
        const facies = group.facies.filter(facies => facies !== polygon.facies)
        if (facies.length > 0) {
          await dispatch('facies/groups/update', { group, facies }, { root: true })
        } else {
          rule.overlayPolygons
            .filter(polygon => getId(polygon.group) === getId(group))
            .forEach(polygon => {
              commit('REMOVE_POLYGON', { rule, polygon })
            })
          await dispatch('facies/groups/remove', group, { root: true })
        }
      }

      // Remove lingering Facies Group (if overlay)
      if (polygon.overlay) {
        const group = rootState.facies.groups.available[`${polygon.group.id}`]
        if (rule.overlayPolygons.filter(polygon => polygon.group.id === group.id).length === 0) {
          await dispatch('facies/groups/remove', group, { root: true })
        }
      }

      // Normalize probabilities again
      await dispatch('normalizeProportionFactors', { rule })
    },
    resetTemplate ({ commit }) {
      commit('CHANGE_TYPE', { type: null })
      commit('CHANGE_TEMPLATE', { template: { text: null } })
    },
    changePreset ({ commit, dispatch, state, rootGetters }, { type, template }) {
      const current = rootGetters.truncationRule
      if (current && type !== state.preset.type && template !== state.preset.template) {
        commit('REMOVE', current.id)
      }
      if (notEmpty(type)) {
        const types = state.templates.types.available
        const typeId = Object.keys(types).find(id => types[`${id}`].name === type)
        commit('CHANGE_TYPE', { type: typeId })
        commit('CHANGE_TEMPLATE', { template: { text: null } })
      }
      if (notEmpty(template)) {
        commit('CHANGE_TEMPLATE', { template })
        dispatch('addRuleFromTemplate')
      }
    },
    changeOrder ({ commit }, { rule, polygon, direction }) {
      const other = rule.polygons.find(_polygon => _polygon.order === polygon.order + direction)
      commit('CHANGE_ORDER', { rule, polygon: other, order: polygon.order })
      commit('CHANGE_ORDER', { rule, polygon, order: polygon.order + direction })
    },
    changeAngles ({ commit }, { rule, polygon, value }) {
      commit('CHANGE_ANGLES', { rule, polygon, value })
    },
    changeProportionFactors ({ commit }, { rule, polygon, value }) {
      commit('CHANGE_PROPORTION_FACTOR', { rule, polygon, value })
    },
    changeSlantFactors ({ commit }, { rule, polygon, value }) {
      commit('CHANGE_FACTORS', { rule, polygon, value })
    },
    async updateRealization ({ commit, dispatch, rootGetters }, rule) {
      await dispatch('facies/normalize', null, { root: true })
      const data = await api.simulateRealization(
        Object.values(rootGetters.fields)
          .map(field => field.specification({ rootGetters })),
        makeTruncationRuleSpecification(rule, rootGetters)
      )
      commit('UPDATE_REALIZATION', { rule, data: data.faciesMap })
      data.fields.forEach(async field => {
        await dispatch('gaussianRandomFields/updateSimulationData', {
          grfId: Object.values(rootGetters.fields).find(item => item.name === field.name).id,
          data: field.data,
        }, { root: true })
      })
    },
    deleteField ({ dispatch, state, rootGetters }, { grfId }) {
      const field = rootGetters.field(grfId)
      return Promise.all(
        Object.values(state.rules)
          .filter(rule => !!rule.fields.some(({ field }) => getId(field) === grfId))
          .map(rule => rule.isUsedInBackground(field)
            ? dispatch('updateBackgroundField', {
              rule,
              index: rule.backgroundFields.indexOf(field),
              field: null,
            })
            : Promise.all(
              rule.overlayPolygons
                .filter(polygon => getId(polygon.field) === grfId)
                .map(polygon => dispatch('updateOverlayField', {
                  rule,
                  polygon,
                  field: null,
                }))
            )
          )
      )
    },
    updateBackgroundField ({ commit }, { rule, index, field }) {
      if (index < 0 || index >= rule.backgroundFields.length) {
        throw new APSError(`The index (${index}) is outside the range of the background fields in the truncation rule with ID ${rule.id}`)
      }
      commit('CHANGE_BACKGROUND_FIELD', { rule, index, field })
    },
    updateOverlayField ({ commit }, { rule, polygon, field }) {
      commit('CHANGE_OVERLAY_FIELD', { rule, polygon, field })
    },
    swapFacies ({ commit }, { rule, polygons }) {
      commit('SET_FACIES', { ruleId: rule.id, polygons: swapFacies(rule, polygons) })
    },
    async updateFacies ({ commit, dispatch, rootState }, { rule, polygon, facies }) {
      if (facies instanceof String) facies = rootState.facies.available[`${facies}`]
      commit('CHANGE_FACIES', { rule, polygon, facies })

      if (!rootState.facies.available[`${facies.id}`].previewProbability) {
        const probability = rule._polygons[`${polygon.id}`].proportion
        await dispatch('facies/updateProbability', { facies, probability }, { root: true })
      }
      await dispatch('normalizeProportionFactors', { rule })
    },
    updateBackgroundGroup ({ commit }, { rule, polygon, group }) {
      commit('UPDATE_BACKGROUND_GROUP', { rule, polygon, value: group })
    },
    update ({ commit }, { rule, polygon, facies }) {
      const polygons = cloneDeep(rule.polygons)
      polygons[polygon.id].group = facies
      commit('CHANGE_POLYGONS', { rule, polygons })
    },
    updateOverlayCenter ({ commit }, { rule, polygon, value }) {
      commit('UPDATE_OVERLAY_CENTER', { rule, polygon, value })
    },
    updateOverlayFraction ({ commit }, { rule, polygon, value }) {
      commit('UPDATE_OVERLAY_FRACTION', { rule, polygon, value })
    },
    toggleOverlay ({ commit }, { rule, value }) {
      commit('CHANGE_OVERLAY_USAGE', { rule, value })
    },
    async normalizeProportionFactors ({ dispatch, rootGetters }, { rule }) {
      const proportional = false /* TODO: should be moved to the state as an option for the user */
      const facies = rule.polygons
        .reduce((obj, polygon) => {
          const id = polygon.facies.id
          if (id) {
            if (!obj.hasOwnProperty(id)) obj[`${id}`] = []
            obj[`${id}`].push(polygon)
          }
          return obj
        }, {})
      await Promise.all(Object.values(facies)
        .map(polygons => {
          const sum = polygons.reduce((sum, polygon) => sum + polygon.fraction, 0)
          return sum !== 1
            ? Promise.all(polygons.map(polygon => dispatch('changeProportionFactors', {
              rule,
              polygon,
              value: isNumber(polygon.fraction) && polygon.fraction > 0 && proportional
                ? polygon.fraction / sum
                : 1 / polygons.length,
            })))
            : new Promise((resolve) => resolve(null))
        })
      )

      // Ensure that facies that has only been assigned to a single polygon have a 'Proportion Factor' of 1
      await Promise.all(rootGetters['facies/selected']
        .map(facies => rule.polygons.filter(polygon => polygon.facies === facies.id))
        .filter(items => items.length === 1)
        .map(items => items[0])
        .map(polygon => dispatch('changeProportionFactors', { rule, polygon, value: 1 })))
    },
    async addRuleFromTemplate ({ dispatch, state }) {
      await dispatch('templates/createRule', { name: state.preset.template, type: state.preset.type })
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.rules, { id, item })
    },
    REMOVE: (state, ruleId) => {
      Vue.delete(state.rules, ruleId)
    },
    ADD_POLYGON: (state, { rule, polygon }) => {
      Vue.set(state.rules[`${rule.id}`]._polygons, polygon.id, polygon)
    },
    REMOVE_POLYGON: (state, { rule, polygon }) => {
      Vue.delete(state.rules[`${rule.id}`]._polygons, polygon.id)
    },
    SET_FACIES: (state, { ruleId, polygons }) => {
      Vue.set(state.rules[`${ruleId}`], '_polygons', polygons)
    },
    UPDATE_REALIZATION: (state, { rule, data }) => {
      Vue.set(state.rules[`${rule.id}`], '_realization', data)
    },
    CHANGE_OVERLAY_USAGE: (state, { rule, value }) => {
      state.rules[`${rule.id}`]._useOverlay = value
    },
    UPDATE_OVERLAY_CENTER: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].center = value
    },
    UPDATE_OVERLAY_FRACTION: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].fraction = value
    },
    UPDATE_BACKGROUND_GROUP: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].group = value
    },
    CHANGE_TYPE: (state, { type }) => changePreset(state, 'type', type),
    CHANGE_TEMPLATE: (state, { template }) => changePreset(state, 'template', template.text),
    CHANGE_FACIES: (state, { rule, polygon, facies }) => {
      Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], 'facies', facies)
    },
    CHANGE_POLYGONS: (state, { rule, polygons }) => {
      setProperty(state, rule, '_polygons', polygons)
    },
    CHANGE_ORDER: (state, { rule, polygon, order }) => {
      state.rules[`${rule.id}`]._polygons[`${polygon.id}`].order = order
    },
    CHANGE_ANGLES: (state, { rule, polygon, value }) => {
      Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], 'angle', value)
    },
    CHANGE_BACKGROUND_FIELD: (state, { rule, index, field }) => {
      state.rules[`${rule.id}`]._backgroundFields.splice(index, 1, field)
    },
    CHANGE_OVERLAY_FIELD: (state, { rule, polygon, field }) => {
      Vue.set(state.rules[`${rule.id}`]._polygons[`${polygon.id}`], 'field', field)
    },
    CHANGE_PROPORTION_FACTOR: (state, { rule, polygon, value }) => {
      setPolygonValue(state, rule, polygon, 'fraction', value)
    },
    CHANGE_FACTORS: (state, { rule, polygon, value }) => {
      setPolygonValue(state, rule, polygon, 'slantFactor', value)
    }
  },

  getters: {
    current (state, getters, rootState, rootGetters) {
      return state.rules
        ? Object.values(state.rules).find(rule => hasCurrentParents(rule, rootGetters))
        : null
    },
    ready (state) {
      return (id) => {
        const rule = id
          ? state.rules[`${id}`]
          : null
        return !!rule && rule.ready
      }
    },
    relevant (state, getters, rootState, rootGetters) {
      return Object.values(state.rules)
        .filter(rule => hasCurrentParents(rule, rootGetters) && hasEnoughFacies(rule, rootGetters))
    },
    typeById (state) {
      return (id) => {
        const rule = state.templates.types.available[`${id}`]
        return rule
          ? rule.type
          : null
      }
    },
    ruleTypes (state, getters, rootState, rootGetters) {
      return Object.values(state.templates.types.available)
        .map(rule => {
          return {
            text: rule.name,
            disabled: !hasEnoughFacies(rule, rootGetters)
          }
        })
    },
    ruleNames (state, getters, rootState, rootGetters) {
      return Object.values(state.templates.available)
        .filter(template => template.type === state.preset.type)
        .sort((a, b) => compareTemplate(rootGetters, a, b))
        .map(template => {
          return {
            text: template.name,
            disabled: !hasEnoughFacies(template, rootGetters)
          }
        })
    },
  },
}
