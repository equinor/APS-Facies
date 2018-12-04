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
    fetch: ({ commit, dispatch, rootGetters }) => {
      return new Promise((resolve, reject) => {
        rms.blockedWellLogParameters(rootGetters.gridModel, rootGetters.blockedWellParameter)
          .then((result) => {
            commit('AVAILABLE', result)
            if (result.length === 1) {
              dispatch('select', result[0]).then(resolve)
            } else if (result.length === 0) {
              dispatch('select', null).then(resolve)
            }
          })
      })
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
