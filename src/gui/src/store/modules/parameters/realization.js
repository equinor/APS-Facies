import Vue from 'vue'
import rms from '@/api/rms'

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
      commit('CURRENT', null)
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
