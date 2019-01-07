import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ commit, dispatch }, blockedWellLog) => {
      commit('CURRENT', blockedWellLog)
      await dispatch('facies/fetch', null, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }) => {
      const result = await rms.blockedWellLogParameters(rootGetters.gridModel, rootGetters.blockedWellParameter)
      commit('AVAILABLE', result)
      if (result.length === 1) {
        await dispatch('select', result[0])
      } else if (result.length === 0) {
        await dispatch('select', null)
      }
    },
  },

  mutations: {
    AVAILABLE: (state, blockedWellLogs) => {
      state.available = blockedWellLogs
    },
    CURRENT: (state, blockedWellLog) => {
      state.selected = blockedWellLog
    },
  },

  getters: {},
}
