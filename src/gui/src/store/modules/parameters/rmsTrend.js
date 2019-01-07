import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
  },

  modules: {},
  actions: {
    async fetch ({ commit, rootGetters }) {
      // TODO: Use 'fetchParameterHelper' to automatically chose the parameter?
      const params = await rms.trendParameters(rootGetters.gridModel)
      commit('AVAILABLE', params)
    },
  },

  mutations: {
    AVAILABLE (state, params) {
      state.available = params
    },
  },
  getters: {},
}
