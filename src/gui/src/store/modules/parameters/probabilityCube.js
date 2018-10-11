import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
  },

  modules: {},

  actions: {
    fetch: ({ commit, rootGetters }) => {
      rms.probabilityCubeParameters(rootGetters.gridModel)
        .then(cubes => commit('AVAILABLE', cubes))
    }
  },

  mutations: {
    AVAILABLE: (state, cubes) => {
      state.available = cubes
    },
  },

  getters: {},
}
