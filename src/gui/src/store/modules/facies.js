import Vue from 'vue'
import rms from 'Api/rms'
import { promiseSimpleCommit } from 'Store/utils'
import { makeData, isEmpty } from 'Utils'
import { Facies } from 'Store/utils/domain'

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
  },

  modules: {},

  actions: {
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
    changed: ({ commit, state }, { facies }) => {
      return promiseSimpleCommit(commit, 'UPDATE', { facies }, () => facies.hasOwnProperty('id'))
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
      state.available = facies
    },
    CURRENT: (state, { id }) => {
      state.current = id
    },
    UPDATE: (state, { facies }) => {
      Vue.set(state.available, facies.id, facies)
    },
    REMOVE: (state, { id }) => {
      Vue.delete(state.available, id)
    },
  },

  getters: {},
}
