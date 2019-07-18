import Vue from 'vue'
import { cloneDeep, isNumber, sample } from 'lodash'

import api from '@/api/rms'

import templates from '@/store/modules/truncationRules/templates'
import preset from '@/store/modules/truncationRules/preset'

import {
  hasCurrentParents,
  minFacies,
  hasEnoughFacies,
  makeTruncationRuleSpecification,
  hasParents,
} from '@/utils'
import { getId, isUUID } from '@/utils/helpers'
import { makeRule } from '@/utils/helpers/processing/templates'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'
import APSTypeError from '@/utils/domain/errors/type'
import APSError from '@/utils/domain/errors/base'
import { makePolygonsFromSpecification, normalizeOrder } from '@/utils/helpers/processing/templates/typed'
import { Cubic, CubicPolygon, Direction } from '@/utils/domain'
import TruncationRule from '@/utils/domain/truncationRule/base'
import { isReady } from '@/store/utils/helpers'

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
    if (
      !(_polygon instanceof CubicPolygon)
      && _polygon.order >= polygon.order
      && _polygon.overlay === polygon.overlay
      && _polygon.atLevel === polygon.atLevel
    ) {
      commit('CHANGE_ORDER', { rule, polygon: _polygon, order: _polygon.order + amount })
    }
  })
}

export default {
  namespaced: true,

  state: {
    rules: {},
  },

  modules: {
    templates,
    preset,
  },

  actions: {
    async fetch ({ dispatch }) {
      await dispatch('templates/fetch')
    },
    async add ({ commit, rootGetters }, rule) {
      if (!(rule instanceof TruncationRule)) {
        rule.backgroundFields = rule.backgroundFields.map(field => rootGetters['gaussianRandomFields/byId'](field))
        rule.polygons.forEach(polygon => {
          polygon.facies = rootGetters['facies/byId'](polygon.facies)
          if (polygon.overlay) {
            polygon.field = rootGetters['gaussianRandomFields/byId'](polygon.field)
            polygon.group = rootGetters['facies/groups/byId'](polygon.group)
          }
        })
        rule.polygons = makePolygonsFromSpecification(rule.polygons)
        rule = makeRule(rule)
      }
      commit('ADD', rule)
    },
    remove ({ commit }, rule) {
      commit('REMOVE', getId(rule))
    },
    async populate ({ dispatch }, { rules, templates, preset }) {
      await dispatch('preset/populate', preset)
      await dispatch('templates/populate', templates)
      await Promise.all(Object.values(rules)
        .map(rule => dispatch('add', rule))
      )
    },
    async addPolygon ({ commit, dispatch, rootState }, { rule, group = '', order = null, overlay = false, parent = null, atLevel = 0 }) {
      if (rule.type === 'bayfill') throw new Error('Bayfill must have exactly 5 polygons. Cannot add more.')

      if (!isNumber(order) || order < 0) {
        const polygons = rule.polygons
          .filter(polygon => (
            polygon.overlay === overlay
            && polygon.atLevel === atLevel
          ))
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
          field = await dispatch('gaussianRandomFields/addEmptyField', rule.parent, { root: true })
        }
        polygon = new OverlayPolygon({ group, field, order })
      } else if (rule.type === 'non-cubic') {
        polygon = new NonCubicPolygon({ order })
      } else if (rule.type === 'cubic') {
        polygon = new CubicPolygon({ order })
        if (parent) {
          commit('ADD_CHILD_POLYGON', { parent, child: polygon })
        }
      } else {
        throw new APSTypeError('Invalid type')
      }
      increaseOrderByRelativeTo({ commit }, rule, polygon)
      commit('ADD_POLYGON', { rule, polygon })
      if (rule instanceof Cubic) {
        normalizeOrder(rule, (polygon, order) => { commit('CHANGE_ORDER', { rule, polygon, order }) })
      }
    },
    async removePolygon ({ commit, dispatch, rootState }, { rule, polygon }) {
      commit('REMOVE_POLYGON', { rule, polygon })
      if (polygon.parent) {
        commit('REMOVE_CHILD', { child: polygon })
      }
      // Decrease the order of polygons
      increaseOrderByRelativeTo({ commit }, rule, polygon, -1)

      // Remove from facies group (if it is no longer a background facies)
      if (!rule.backgroundPolygons.map(({ facies }) => getId(facies)).includes(getId(polygon.facies))) {
        const group = Object.values(rootState.facies.groups.available).find(group => group.has(polygon.facies))
        if (group) {
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
    async split ({ dispatch }, { rule, polygon, value }) {
      if (!(rule instanceof Cubic)) throw new APSTypeError('Only Cubic truncation rules may use \'split\'')

      await Promise.all([...Array(value)]
        .map((_, index) => dispatch('addPolygon', { rule, parent: polygon, order: index + 1 }))
      )
    },
    async merge ({ dispatch }, { rule, polygons }) {
      if (!(rule instanceof Cubic)) throw new APSTypeError('Only Cubic truncation rules may use \'merge\'')

      const parent = sample(polygons.map(({ parent }) => parent))
      if (polygons.every(polygon => getId(polygon.parent) === getId(parent))) {
        await Promise.all(polygons.map(polygon => dispatch('removePolygon', { rule, polygon })))
        if (parent.children.length !== 0) {
          await dispatch('addPolygon', { rule, parent, atLevel: parent.atLevel + 1 })
        }
      } else {
        throw new APSTypeError('Polygons need to have the same parent in order to be merged')
      }
    },
    changeOrder ({ commit }, { rule, polygon, direction }) {
      const other = rule.polygons.find(_polygon => _polygon.order === polygon.order + direction)
      if (!(other instanceof CubicPolygon)) {
        commit('CHANGE_ORDER', { rule, polygon: other, order: polygon.order })
      }
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
    changeDirection ({ commit }, { rule, value }) {
      commit('CHANGE_DIRECTION', { rule, value: new Direction(value) })
    },
    async updateRealization ({ commit, dispatch, rootGetters }, rule) {
      await dispatch('facies/normalize', undefined, { root: true })
      const { fields, faciesMap: data } = await api.simulateRealization(
        rule.fields
          .map(field => field.specification({ rootGetters })),
        makeTruncationRuleSpecification(rule, rootGetters)
      )
      commit('UPDATE_REALIZATION', { rule, data })
      await Promise.all(fields.map(field => {
        return dispatch('gaussianRandomFields/updateSimulationData', {
          grfId: rule.fields.find(item => item.name === field.name).id,
          data: field.data,
        }, { root: true })
      }))
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
    async updateFacies ({ commit, dispatch, rootState }, { rule, polygon, facies }) {
      if (facies instanceof String) facies = rootState.facies.available[`${facies}`]
      commit('CHANGE_FACIES', { rule, polygon, facies })

      if (!rootState.facies.available[`${facies.id}`].previewProbability) {
        const probability = rule._polygons[`${polygon.id}`].fraction
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
    async toggleOverlay ({ commit, dispatch, rootState }, { rule, value }) {
      // If there are too few GRFs, add more
      const availableFields = Object.values(rootState.gaussianRandomFields.fields)
        .filter(field => hasParents(field, rule.parent.zone, rule.parent.region))
      if (availableFields.length <= rule.backgroundFields.length) {
        await dispatch('gaussianRandomFields/addEmptyField', rule.parent, { root: true })
      }
      commit('CHANGE_OVERLAY_USAGE', { rule, value })
    },
    async normalizeProportionFactors ({ dispatch, rootGetters }, { rule }) {
      const proportional = false /* TODO: should be moved to the state as an option for the user */
      const facies = rule.polygons
        .reduce((obj, polygon) => {
          const id = getId(polygon.facies)
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
    ADD: (state, rule) => {
      Vue.set(state.rules, rule.id, rule)
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
    REMOVE_CHILD: (state, { child }) => {
      Vue.delete(child.parent.children, child.parent.children.findIndex(polygon => getId(polygon) === getId(child)))
    },
    SET_FACIES: (state, { ruleId, polygons }) => {
      Vue.set(state.rules[`${ruleId}`], '_polygons', polygons)
    },
    UPDATE_REALIZATION: (state, { rule, data }) => {
      Vue.set(state.rules[`${rule.id}`], 'realization', data)
    },
    CHANGE_OVERLAY_USAGE: (state, { rule, value }) => {
      state.rules[`${rule.id}`]._useOverlay = value
    },
    UPDATE_OVERLAY_CENTER: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].center = value
    },
    UPDATE_BACKGROUND_GROUP: (state, { rule, polygon, value }) => {
      state.rules[rule.id]._polygons[polygon.id].group = value
    },
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
    },
    CHANGE_DIRECTION: (state, { rule, value }) => {
      Vue.set(state.rules[`${rule.id}`], 'direction', value)
    },
    ADD_CHILD_POLYGON: (state, { parent, child }) => {
      parent.children.push(child)
      Vue.set(child, 'parent', parent)
    }
  },

  getters: {
    current (state, getters, rootState, rootGetters) {
      return state.rules
        ? Object.values(state.rules).find(rule => hasCurrentParents(rule, rootGetters))
        : null
    },
    ready (state, getters, rootState, rootGetters) {
      return (rule) => {
        rule = isUUID(rule)
          ? state.rules[`${getId(rule)}`]
          : rule
        return (
          !rootGetters['copyPaste/isPasting'](rule.parent)
          && isReady({ rootGetters, rootState }, rule)
        )
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
        .sort((a, b) => a.order - b.order)
        .map(rule => {
          return {
            text: rule.name,
            disabled: !hasEnoughFacies(rule, rootGetters),
            order: rule.order,
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
