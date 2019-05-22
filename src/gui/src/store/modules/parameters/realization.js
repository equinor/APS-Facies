import Vue from 'vue'
import rms from '@/api/rms'

import { DEFAULT_FACIES_REALIZATION_PARAMETER_NAME } from '@/config'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({ commit }, parameter) => {
      commit('CURRENT', parameter)
    },
    fetch: async ({ commit, rootGetters }) => {
      commit('CURRENT', DEFAULT_FACIES_REALIZATION_PARAMETER_NAME)
      const discreteParameters = await rms.realizationParameters(rootGetters.gridModel)
      commit('AVAILABLE', discreteParameters)
      return discreteParameters
    },
  },

  mutations: {
    AVAILABLE: (state, parameters) => {
      Vue.set(state, 'available', parameters)
    },
    CURRENT: (state, parameter) => {
      state.selected = parameter
    },
  },

  getters: {},
}
