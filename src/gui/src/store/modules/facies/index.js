import Vue from 'vue'

import math from 'mathjs'

import { cloneDeep, merge, isEqual } from 'lodash'

import { Facies } from '@/store/utils/domain'
import {
  isEmpty,
  notEmpty,
  hasCurrentParents,
  hasParents,
  parentId,
  makeData,
} from '@/utils'
import { promiseSimpleCommit, changeFacies } from '@/store/utils'

import { SELECTED_ITEMS } from '@/store/mutations'
import global from './global'
import { isUUID } from '@/utils/typing'

const updateFaciesProbability = (dispatch, facies, probability) => dispatch('changed', { id: facies.id, previewProbability: probability })

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
          return new Facies({ facies: global.id, ...parent })
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
  },

  actions: {
    select: ({ commit, state }, { items, parent }) => {
      const facies = updateSelected(state.global.available, state.available, items, parent)
      commit('AVAILABLE', facies)
      return Promise.resolve(Object.keys(facies))
    },
    populate: ({ commit }, facies) => {
      facies = makeData(facies, Facies)
      commit('AVAILABLE', facies)
    },
    removeSelectedFacies: ({ commit, dispatch, state }) => {
      return promiseSimpleCommit(commit, 'REMOVE', { id: state.current }, () => !!state.current)
        .then(() => {
          dispatch('current', { id: null })
        })
    },
    updateProbabilities: ({ dispatch, state }, { facies, probabilityCubes }) => {
      if (notEmpty(probabilityCubes) && isEmpty(facies)) {
        Object.keys(probabilityCubes)
          .map(parameter => {
            const facies = Object.values(state.available).find(facies => facies.probabilityCube === parameter)
            return updateFaciesProbability(dispatch, facies, probabilityCubes[`${parameter}`])
          })
      }
      dispatch('normalizeEmpty')
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
      selectedFacies
        .map(facies => facies.previewProbability === 0 || facies.previewProbability === null ? updateFaciesProbability(dispatch, facies, emptyProbability) : null)
    },
    normalize: ({ dispatch, state, getters }) => {
      const selected = getters.selected
      const cumulativeProbability = selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
      selected.forEach(facies => {
        const probability = cumulativeProbability === 0
          ? math.divide(1, selected.length)
          : math.divide(facies.previewProbability, cumulativeProbability)
        updateFaciesProbability(dispatch, facies, probability)
      })
    },
    populateConstantProbability: ({ commit }, data) => {
      Object.keys(data).forEach(parentId => {
        commit('CONSTANT_PROBABILITY', { parentId, toggled: data[`${parentId}`] })
      })
    },
    toggleConstantProbability: ({ commit, state, getters, rootGetters }) => {
      const _id = parentId({ zone: rootGetters.zone, region: rootGetters.region })
      const usage = !getters.constantProbability()
      commit('CONSTANT_PROBABILITY', { parentId: _id, toggled: usage })
    },
    setConstantProbability: ({ commit, state }, value) => {
      if (typeof value === 'boolean') {
        commit('CONSTANT_PROBABILITY', value)
      }
    },
    changed: (context, facies) => changeFacies(context, facies),
    fetch: async ({ dispatch }) => {
      await dispatch('global/fetch')
    },
  },

  mutations: {
    AVAILABLE: (state, facies) => {
      Vue.set(state, 'available', facies)
    },
    SELECTED: SELECTED_ITEMS,
    UPDATE: (state, facies) => {
      Vue.set(state.available, facies.id, facies)
    },
    REMOVE: (state, { id }) => {
      Vue.delete(state.available, id)
    },
    CONSTANT_PROBABILITY: (state, { parentId, toggled }) => {
      Vue.set(state.constantProbability, parentId, toggled)
    },
  },

  getters: {
    nameById: (state, getters) => (id) => {
      id = isUUID(id) ? id : id.id
      const facies = getters.byId(id)
      return facies.name || getters.byId(facies.facies).name
    },
    byId: (state) => (id) => {
      return state.available[`${id}`] || state.global.available[`${id}`]
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
      return Object.values(state.available).filter(facies => hasCurrentParents(facies, rootGetters))
    },
    cumulative: (state, getters) => {
      return getters.selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
    }
  },
}
