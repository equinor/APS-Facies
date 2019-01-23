import Vue from 'vue'

import rms from '@/api/rms'

const parametersDependentOnGrid = [
  'region',
  'blockedWell',
  'rmsTrend',
  'probabilityCube',
  'grid',
  'realization',
]

export default {
  namespaced: true,

  state: {
    available: [],
    current: null,
  },

  actions: {
    select: async ({ state, commit, dispatch, rootState }, gridModel) => {
      if (state.available.includes(gridModel)) {
        commit('CURRENT', gridModel)
        // when loading a file, we must ensure that all promises in this method are resolved before calling the
        // next method in the loading chain. The loading chain depends on the fetch statements in this methods being
        // resolved
        await dispatch('zones/fetch', null, { root: true })
        await Promise.all(parametersDependentOnGrid.map(param => dispatch(`parameters/${param}/fetch`, null, { root: true })))
        return gridModel
      } else {
        throw new Error(`Selected grid model ( ${gridModel} ) is not present in the current project.

Tip: GridModelName in the APS model file must be one of { ${state.available.join()} }`)
      }
    },
    fetch: ({ commit }) => {
      return rms.gridModels().then(result => {
        commit('AVAILABLE', result)
      })
    }
  },

  mutations: {
    CURRENT: (state, selectedGridModel) => {
      Vue.set(state, 'current', selectedGridModel)
    },
    AVAILABLE: (state, gridModels) => {
      state.available = gridModels
    },
  },

  getters: {},
}
