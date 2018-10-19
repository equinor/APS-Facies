import Vue from 'vue'

import templates from '@/store/modules/truncationRules/templates'
import { Bayfill } from '@/store/utils/domain/truncationRule'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import { notEmpty, hasCurrentParents, hasEnoughFacies, resolve } from '@/utils'

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
    add ({ commit, state, rootGetters }, { type, polygons, fields, settings }) {
      type = state.templates.types.available[`${type}`].type
      let rule
      fields = processFields(rootGetters, fields)
      polygons = processPolygons(rootGetters, polygons)
      if (type === 'bayfill') {
        rule = new Bayfill({ polygons, fields, settings, zone: rootGetters.zone, region: rootGetters.region })
      } else if (type === 'non-cubic') {
        // TODO
      } else if (type === 'cubic') {
        // TODO
      } else {
        throw new Error(`The truncation rule of type ${type} is not implemented`)
      }
      return addItem({ commit }, { item: rule })
    },
    changePreset ({ commit, dispatch, state }, { type, template }) {
      if (notEmpty(type)) {
        const types = state.templates.types.available
        const typeId = Object.keys(types).find(id => types[`${id}`].name === type)
        commit('CHANGE_TYPE', { type: typeId })
      }
      if (notEmpty(template)) {
        commit('CHANGE_TEMPLATE', { template })
        dispatch('changeRule')
      }
    },
    changeFactors ({ commit, rootGetters }, { polygon, value }) {
      const current = rootGetters.truncationRule
      const mapping = {
        'Floodplain': 'SF',
        'Subbay': 'YSF',
        'Bayhead Delta': 'SBHD',
      }
      const index = current.settings.findIndex(item => item.name === mapping[`${polygon.name}`])
      if (index >= 0) {
        commit('CHANGE_FACTORS', { ruleId: current.id, index, value })
      } else {
        throw new Error(`The ${polygon.name} polygon was not found`)
      }
    },
    updateFields ({ commit, rootGetters }, { channel, selected }) {
      commit('CHANGE_FIELDS', { ruleId: rootGetters.truncationRule.id, channel, fieldId: selected })
    },
    updateFacies ({ commit, dispatch, state, rootState }, { rule, polygon, faciesId }) {
      const polygonName = polygon.name || polygon
      commit('CHANGE_FACIES', { ruleId: rule.id || rule, polygonName, faciesId })

      if (!rootState.facies.available[`${faciesId}`].previewProbability) {
        const probability = rule.polygons.find(polygon => polygon.name === polygonName).proportion
        dispatch('facies/updateProbability', { facies: faciesId, probability }, { root: true })
      }
    },
    changeRule ({ commit, dispatch, state, rootGetters }) {
      const rule = Object.values(state.templates.available).find(template => template.name === state.preset.template && template.type === state.preset.type)
      const missing = rule.minFields - Object.values(rootGetters.fields).length
      if (missing > 0) {
        for (let i = 0; i < missing; i++) dispatch('gaussianRandomFields/addEmptyField', {}, { root: true })
      }
      dispatch('add', { ...rule, type: state.preset.type })
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
    CHANGE_TYPE: (state, { type }) => changePreset(state, 'type', type),
    CHANGE_TEMPLATE: (state, { template }) => changePreset(state, 'template', template),
    CHANGE_FACIES: (state, { ruleId, polygonName, faciesId }) => {
      state.rules[`${ruleId}`].polygons.find(polygon => polygon.name === polygonName).facies = faciesId
    },
    CHANGE_FIELDS: (state, { ruleId, channel, fieldId }) => {
      state.rules[`${ruleId}`].fields.find(field => field.channel === channel).field = fieldId
    },
    CHANGE_FACTORS: (state, { ruleId, index, value }) => {
      Vue.set(state.rules[`${ruleId}`].settings[`${index}`], 'factor', value)
    }
  },

  getters: {
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
