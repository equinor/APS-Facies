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
    async fetch ({ dispatch, rootGetters }) {
      const simBox = await api.simulationBoxOrigin(rootGetters.gridModel)
      await dispatch('populate', simBox)
      return simBox.rotation
    },
    populate ({ commit }, { size, origin }) {
      commit('SIZE', size)
      commit('ORIGIN', origin)
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
