import Vue from 'vue'

import math from 'mathjs'

import rms from '@/api/rms'

import { Facies } from '@/store/utils/domain'
import { makeData, selectItems, isEmpty, notEmpty } from '@/utils'
import { promiseSimpleCommit } from '@/store/utils'

import { SELECTED_ITEMS } from '@/store/mutations'

const updateFaciesProbability = (dispatch, facies, probability) => dispatch('changed', {
  facies: new Facies({
    _id: facies.id,
    ...facies,
    previewProbability: probability,
  })
})

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
    constantProbability: false,
  },

  modules: {},

  actions: {
    select: ({ commit, state }, items) => {
      const facies = selectItems({ state, items, _class: Facies })
      commit('AVAILABLE', { facies })
      return Promise.resolve(Object.keys(facies))
    },
    current: ({ commit }, { id }) => {
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    removeSelectedFacies: ({ commit, dispatch, state }) => {
      return promiseSimpleCommit(commit, 'REMOVE', { id: state.current }, () => !!state.current)
        .then(() => {
          dispatch('current', { id: null })
        })
    },
    new: ({ dispatch, state, rootState }, { code, name, color }) => {
      if (isEmpty(code) || code < 0) {
        // TODO: Find the highest values in the Global Facies Table (from rms, as some may have been deleted)
        code = 1 + Object.values(state.available)
          .map(facies => facies.code)
          .reduce((a, b) => Math.max(a, b), 0)
      }
      if (isEmpty(name)) {
        name = `F${code}`
      }
      if (isEmpty(color)) {
        const colors = rootState.constants.faciesColors.available
        color = colors[code % colors.length]
      }
      dispatch('changed', { facies: new Facies({ code, name, color }) })
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
    normalizeEmpty: ({ dispatch, getters }) => {
      const selectedFacies = getters.selected
      const probabilities = selectedFacies
        .map(facies => facies.previewProbability ? facies.previewProbability : 0)
      const emptyProbability = (1 - probabilities.reduce((sum, prob) => sum + prob, 0)) / probabilities.filter(prob => prob === 0).length
      selectedFacies
        .map(facies => facies.previewProbability === 0 || facies.previewProbability === null ? updateFaciesProbability(dispatch, facies, emptyProbability) : null)
    },
    normalize: ({ dispatch, getters }) => {
      const selected = getters.selected
      const cumulativeProbability = selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
      selected.map(facies => {
        const probability = cumulativeProbability === 0
          ? math.divide(1, selected.length)
          : math.divide(facies.previewProbability, cumulativeProbability)
        updateFaciesProbability(dispatch, facies, probability)
      })
    },
    toggleConstantProbability: ({ commit, state }) => {
      commit('CONSTANT_PROBABILITY', !state.constantProbability)
    },
    changed: ({ commit, state }, { facies }) => {
      return promiseSimpleCommit(commit, 'UPDATE', { facies: new Facies({ _id: facies.id, ...facies }) }, () => facies.hasOwnProperty('id'))
    },
    fetch: ({ commit, rootGetters, rootState }) => {
      return rms.facies(rootGetters.gridModel, rootGetters.blockedWellParameter, rootGetters.blockedWellLogParameter)
        .then(facies => {
          // TODO: Add colors (properly)
          for (let i = 0; i < facies.length; i++) {
            facies[i].color = rootState.constants.faciesColors.available[i]
          }
          const data = makeData(facies, Facies)
          commit('AVAILABLE', { facies: data })
        })
    },
  },

  mutations: {
    AVAILABLE: (state, { facies }) => {
      Vue.set(state, 'available', facies)
    },
    CURRENT: (state, { id }) => {
      state.current = id
    },
    SELECTED: SELECTED_ITEMS,
    UPDATE: (state, { facies }) => {
      Vue.set(state.available, facies.id, facies)
    },
    REMOVE: (state, { id }) => {
      Vue.delete(state.available, id)
    },
    CONSTANT_PROBABILITY: (state, toggled) => {
      state.constantProbability = toggled
    },
  },

  getters: {
    selected: (state) => {
      return Object.values(state.available).filter(facies => facies.selected)
    },
    cumulative: (state, getters) => {
      return getters.selected.map(facies => facies.previewProbability).reduce((sum, prob) => sum + prob, 0)
    }
  },
}
