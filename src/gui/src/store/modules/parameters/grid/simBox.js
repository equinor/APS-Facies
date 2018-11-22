import api from '@/api/rms'

export default {
  namespaced: true,
  state: {
    size: {
      x: null, y: null, z: null,
    },
    origin: {
      x: null, y: null,
    },
  },
  actions: {
    async fetch ({ commit, rootGetters }) {
      const simBox = await api.simulationBoxOrigin(rootGetters.gridModel)
      // TODO: Simbox Z and gird Z is zone dependent
      commit('SIZE', simBox.size)
      commit('ORIGIN', simBox.origin)
      return simBox.rotation
    },
    thickness ({ commit }, zoneName) {},
  },
  mutations: {
    SIZE: (state, { x, y, z }) => {
      state.size.x = x
      state.size.y = y
      state.size.z = z
    },
    ORIGIN: (state, { x, y }) => {
      state.origin.x = x
      state.origin.y = y
    },
  },
  getters: {},
}
