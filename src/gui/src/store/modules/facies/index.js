import Vue from 'vue'

import math from 'mathjs'

import { cloneDeep, merge, isEqual, isNumber } from 'lodash'

import Facies from '@/utils/domain/facies/local'
import {
  notEmpty,
  hasCurrentParents,
  hasParents,
  parentId,
  makeData,
} from '@/utils'

import { SELECTED_ITEMS } from '@/store/mutations'
import global from './global'
import groups from './groups'
import { getId, isUUID } from '@/utils/helpers'

const updateFaciesProbability = (dispatch, facies, probability) => dispatch('changePreviewProbability', { facies, previewProbability: probability })

const _removeCurrent = (items, parent) => {
  return Object.values(items)
    .filter(item => !hasParents(item, parent.zone, parent.region))
    .reduce((obj, item) => {
      obj[`${item.id}`] = item
      return obj
    }, {})
}

const updateSelected = (globalFacies, localFacies, selected, parent) => {
  return merge(
    _removeCurrent(cloneDeep(localFacies), parent),
    selected
      .map(global => {
        const existing = Object.values(localFacies).find((local) => local.facies === global.id && isEqual(local.parent, parent))
        if (existing) {
          return existing
        } else {
          return new Facies({ facies: globalFacies[global.id], ...parent })
        }
      })
      .reduce((obj, facies) => {
        obj[`${facies.id}`] = facies
        return obj
      }, {})
  )
}

export default {
  namespaced: true,

  state: {
    available: {},
    constantProbability: {},
  },

  modules: {
    global,
    groups,
  },

  actions: {
    add: ({ commit }, { facies, parent, probabilityCube = null, previewProbability = null }) => {
      const localFacies = new Facies({
        facies,
        probabilityCube,
        previewProbability,
        parent,
      })
      commit('ADD', { facies: localFacies })
      return localFacies
    },
    select: ({ commit, state }, { items, parent }) => {
      const facies = updateSelected(state.global.available, state.available, items, parent)
      commit('AVAILABLE', facies)
      return Promise.resolve(Object.keys(facies))
    },
    populate: ({ commit, state }, facies) => {
      facies = makeData(facies, Facies, state.available)
      commit('AVAILABLE', facies)
    },
    updateProbabilities: async ({ dispatch, state }, { probabilityCubes }) => {
      if (notEmpty(probabilityCubes)) {
        for (const parameter in probabilityCubes) {
          const facies = Object.values(state.available)
            .filter(facies => facies.probabilityCube === parameter)
          await Promise.all(facies.map(facies => updateFaciesProbability(dispatch, facies, probabilityCubes[`${parameter}`])))
        }
      }
      await dispatch('normalizeEmpty')
    },
    updateProbability: ({ dispatch, state, getters }, { facies, probability }) => {
      if (!facies.id) {
        facies = state.available[`${facies}`] || getters.selected.find(item => item.facies === facies)
      }
      return updateFaciesProbability(dispatch, facies, probability)
    },
    normalizeEmpty: ({ dispatch, getters }) => {
      const selectedFacies = getters.selected
      const probabilities = selectedFacies
        .map(facies => facies.previewProbability ? facies.previewProbability : 0)
      const emptyProbability = (1 - probabilities.reduce((sum, prob) => sum + prob, 0)) / probabilities.filter(prob => prob === 0).length
      return Promise.all(selectedFacies
        .map(facies => facies.previewProbability === 0 || facies.previewProbability === null
          ? updateFaciesProbability(dispatch, facies, emptyProbability)
          : new Promise((resolve) => resolve()))
      )
    },
    normalize: ({ dispatch, getters }) => {
      const selected = getters.selected
      const cumulativeProbability = selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
      return Promise.all(selected.map(facies => {
        const probability = cumulativeProbability === 0
          ? math.divide(1, selected.length)
          : math.divide(facies.previewProbability, cumulativeProbability)
        return updateFaciesProbability(dispatch, facies, probability)
      }))
    },
    populateConstantProbability: ({ commit }, data) => {
      Object.keys(data).forEach(parentId => {
        commit('CONSTANT_PROBABILITY', { parentId, toggled: data[`${parentId}`] })
      })
    },
    toggleConstantProbability: ({ commit, getters, rootGetters }) => {
      const _id = parentId({ zone: rootGetters.zone, region: rootGetters.region })
      const usage = !getters.constantProbability()
      commit('CONSTANT_PROBABILITY', { parentId: _id, toggled: usage })
    },
    setConstantProbability: ({ commit }, { parentId, toggled }) => {
      if (typeof value === 'boolean') {
        commit('CONSTANT_PROBABILITY', { parentId, toggled })
      }
    },
    changeProbabilityCube: ({ commit }, { facies, probabilityCube }) => {
      commit('CHANGE_PROBABILITY_CUBE', { facies, probabilityCube })
    },
    changePreviewProbability: ({ commit }, { facies, previewProbability }) => {
      commit('CHANGE_PREVIEW_PROBABILITY', { facies, previewProbability })
    },
    fetch: async ({ dispatch }) => {
      await dispatch('global/fetch')
    },
  },

  mutations: {
    ADD: (state, { facies }) => {
      Vue.set(state.available, facies.id, facies)
    },
    AVAILABLE: (state, facies) => {
      Vue.set(state, 'available', facies)
    },
    SELECTED: SELECTED_ITEMS,
    UPDATE: (state, facies) => {
      Vue.set(state.available, facies.id, facies)
    },
    CONSTANT_PROBABILITY: (state, { parentId, toggled }) => {
      Vue.set(state.constantProbability, parentId, toggled)
    },
    CHANGE_PROBABILITY_CUBE: (state, { facies, probabilityCube }) => {
      state.available[`${facies.id}`].probabilityCube = probabilityCube
    },
    CHANGE_PREVIEW_PROBABILITY: (state, { facies, previewProbability }) => {
      state.available[`${facies.id}`].previewProbability = previewProbability
    },
  },

  getters: {
    name: (state, getters) => (id) => {
      id = isUUID(id) ? id : id.id
      const facies = getters.byId(id)
      if (facies instanceof Array) {
        return facies.map(id => getters.name(id))
      }
      return facies.name || getters.byId(facies.facies).name
    },
    byId: (state, getters) => (id) => {
      id = getId(id)
      const facies = state.available[`${id}`] || state.global.available[`${id}`]
      if (!facies) {
        const group = getters['groups/byId'](id)
        return group && group.facies.map(getters.byId)
      } else {
        return facies
      }
    },
    byName: (state) => (name) => {
      return Object.values(state.available).find(facies => facies.name === name)
    },
    constantProbability: (state, getters, rootState, rootGetters) => parent => {
      parent = parent || { zone: rootGetters.zone, region: rootGetters.region }
      const constantProbability = () => state.constantProbability[`${parentId(parent)}`]
      return !parent.zone || typeof constantProbability() === 'undefined'
        ? true
        : constantProbability()
    },
    selected: (state, getters, rootState, rootGetters) => {
      return Object.values(state.available)
        .filter(facies => hasCurrentParents(facies, rootGetters))
        .sort((a, b) => a.facies.code - b.facies.code)
    },
    cumulative: (state, getters) => {
      return getters.selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
    },
    unset: (state, getters) => {
      return getters.selected.every(facies => !isNumber(facies.previewProbability))
    }
  },
}
