import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
  },

  modules: {},
  actions: {
    fetch ({commit, rootGetters}) {
      // TODO: Use 'fetchParameterHelper' to automatically chose the parameter?
      return rms.trendParameters(rootGetters.gridModel)
        .then(params => {
          commit('AVAILABLE', params)
        })
    },
  },

  mutations: {
    AVAILABLE (state, params) {
      state.available = params
    },
  },
  getters: {},
}
