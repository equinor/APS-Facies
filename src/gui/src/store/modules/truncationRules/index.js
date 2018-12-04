import Vue from 'vue'

import cloneDeep from 'lodash/cloneDeep'

import api from '@/api/rms'

import templates from '@/store/modules/truncationRules/templates'

import { Bayfill } from '@/store/utils/domain/truncationRule'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import { notEmpty, hasCurrentParents, hasParents, hasEnoughFacies, resolve, allSet, makeTruncationRuleSpecification } from '@/utils'

const changePreset = (state, thing, item) => {
  Vue.set(state.preset, thing, item)
}

const process = (getters, items, target, type, path) => {
  return items.map(item => {
    const updated = {
      ...item,
    }
    updated[`${target}`] = getters.id(type, resolve(path, item))
    return updated
  })
}

const processFields = (getters, fields) => {
  return process(getters, fields, 'field', 'gaussianRandomField', 'field.name')
}

const processPolygons = (getters, polygons) => {
  return process(getters, polygons, 'facies', 'facies', 'facies')
}

const findPolygonInRule = (rule, polygon) => {
  return rule.polygons[`${polygon.id}`]
}

const setFacies = (polygons, src, dest) => {
  polygons[`${dest.id}`].facies = src.facies
}

function swapFacies (rule, polygons) {
  if (polygons.length !== 2) throw new Error('Only two polygons may be swapped')
  const newPolygons = cloneDeep(rule.polygons)

  const first = findPolygonInRule(rule, polygons[0])
  const other = findPolygonInRule(rule, polygons[1])

  setFacies(newPolygons, first, other)
  setFacies(newPolygons, other, first)

  return newPolygons
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
    add ({ commit, state, rootGetters }, { type, polygons, fields, settings, parent }) {
      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }
      type = state.templates.types.available[`${type}`].type
      let rule
      fields = processFields(rootGetters, fields)
      polygons = processPolygons(rootGetters, polygons)
      if (type === 'bayfill') {
        rule = new Bayfill({ polygons, fields, settings, ...parent })
      } else if (type === 'non-cubic') {
        // TODO
      } else if (type === 'cubic') {
        // TODO
      } else {
        throw new Error(`The truncation rule of type ${type} is not implemented`)
      }
      return addItem({ commit }, { item: rule })
    },
    changePreset ({ commit, dispatch, state }, { type, template, parent }) {
      if (notEmpty(type)) {
        const types = state.templates.types.available
        const typeId = Object.keys(types).find(id => types[`${id}`].name === type)
        commit('CHANGE_TYPE', { type: typeId })
      }
      if (notEmpty(template)) {
        commit('CHANGE_TEMPLATE', { template })
        dispatch('changeRule', parent)
      }
    },
    changeFactors ({ commit, rootGetters }, { polygon, value }) {
      const current = rootGetters.truncationRule
      if (current.settings.hasOwnProperty(polygon.id)) {
        commit('CHANGE_FACTORS', { ruleId: current.id, polygonId: polygon.id, value })
      } else {
        throw new Error(`The ${polygon.name} polygon was not found`)
      }
    },
    async updateRealization ({ commit, dispatch, rootGetters }, rule) {
      const data = await api.simulateRealization(
        Object.values(rootGetters.fields),
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
    updateFields ({ commit, rootGetters }, { channel, selected }) {
      commit('CHANGE_FIELDS', { ruleId: rootGetters.truncationRule.id, channel, fieldId: selected })
    },
    swapFacies ({ commit }, { rule, polygons }) {
      commit('SET_FACIES', { ruleId: rule.id, polygons: swapFacies(rule, polygons) })
    },
    updateFacies ({ commit, dispatch, state, rootState }, { rule, polygon, faciesId }) {
      const polygonId = polygon.id || polygon
      commit('CHANGE_FACIES', { ruleId: rule.id || rule, polygonId, faciesId })

      if (!rootState.facies.available[`${faciesId}`].previewProbability) {
        const probability = rule.polygons[`${polygonId}`].proportion
        dispatch('facies/updateProbability', { facies: faciesId, probability }, { root: true })
      }
    },
    changeRule ({ commit, dispatch, state, rootState, rootGetters }, parent) {
      const rule = Object.values(state.templates.available).find(template => template.name === state.preset.template && template.type === state.preset.type)
      let missing = 0
      if (parent) {
        const existingFields = Object.values(rootState.gaussianRandomFields.fields)
          .filter(field => hasParents(field, parent.zone, parent.region))
        missing = rule.minFields - existingFields.length
      } else {
        missing = rule.minFields - Object.values(rootGetters.fields).length
      }
      if (missing > 0) {
        for (let i = 0; i < missing; i++) dispatch('gaussianRandomFields/addEmptyField', {}, { root: true })
      }
      dispatch('add', { ...rule, type: state.preset.type, parent })
      rule.polygons.forEach(polygon => {
        if (polygon.facies && polygon.proportion >= 0) {
          const facies = rootGetters['facies/byName'](polygon.facies)
          dispatch('facies/updateProbability', { facies, probability: polygon.proportion }, { root: true })
        }
      })
    }
  },

  mutations: {
    ADD: (state, { id, item }) => {
      ADD_ITEM(state.rules, { id, item })
    },
    SET_FACIES: (state, { ruleId, polygons }) => {
      Vue.set(state.rules[`${ruleId}`], 'polygons', polygons)
    },
    UPDATE_REALIZATION: (state, { rule, data }) => {
      Vue.set(state.rules[`${rule.id}`], '_realization', data)
    },
    CHANGE_TYPE: (state, { type }) => changePreset(state, 'type', type),
    CHANGE_TEMPLATE: (state, { template }) => changePreset(state, 'template', template),
    CHANGE_FACIES: (state, { ruleId, polygonId, faciesId }) => {
      state.rules[`${ruleId}`].polygons[`${polygonId}`].facies = faciesId
    },
    CHANGE_FIELDS: (state, { ruleId, channel, fieldId }) => {
      state.rules[`${ruleId}`].fields.find(field => field.channel === channel).field = fieldId
    },
    CHANGE_FACTORS: (state, { ruleId, polygonId, value }) => {
      Vue.set(state.rules[`${ruleId}`].settings[`${polygonId}`], 'factor', value)
    }
  },

  getters: {
    ready (state) {
      return (id) => {
        const rule = id
          ? state.rules[`${id}`]
          : null
        return !!rule &&
               allSet(rule.fields, 'field') &&
               allSet(rule.polygons, 'facies')
      }
    },
    relevant (state, getters, rootState, rootGetters) {
      return Object.values(state.rules)
        .filter(rule => hasCurrentParents(rule, rootGetters) && hasEnoughFacies(rule, rootGetters))
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
    ruleNames (state) {
      return Object.values(state.templates.available).filter(template => template.type === state.preset.type).map(template => template.name)
    },
  },
}
