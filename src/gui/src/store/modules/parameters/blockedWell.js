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
    fetch: ({ commit, dispatch, rootGetters }) => {
      return new Promise((resolve, reject) => {
        rms.blockedWellParameters(rootGetters.gridModel)
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
    AVAILABLE: (state, blockedWells) => {
      state.available = blockedWells
    },
    CURRENT: (state, blockedWell) => {
      state.selected = blockedWell
    },
  },

  getters: {},
}
