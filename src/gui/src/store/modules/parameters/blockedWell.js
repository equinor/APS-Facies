import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ commit, dispatch }, blockedWell) => {
      commit('CURRENT', blockedWell)
      await dispatch('parameters/blockedWellLog/fetch', null, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }) => {
      const result = await rms.blockedWellParameters(rootGetters.gridModel)
      commit('AVAILABLE', result)
      if (result.length === 1) {
        await dispatch('select', result[0])
      } else if (result.length === 0) {
        await dispatch('select', null)
      }
    },
  },

  mutations: {
    AVAILABLE: (state, blockedWells) => {
      state.available = blockedWells
    },
    CURRENT: (state, blockedWell) => {
      state.selected = blockedWell
    },
  },

  getters: {},
}
