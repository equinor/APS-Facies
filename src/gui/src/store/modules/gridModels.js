import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    current: null,
  },

  actions: {
    select: ({ state, commit, dispatch, rootState }, gridModel) => {
      return new Promise((resolve, reject) => {
        if (state.available.includes(gridModel)) {
          commit('CURRENT', gridModel)
          const parameters = ['zone', 'region', 'blockedWell', 'rmsTrend', 'probabilityCube']
          parameters.forEach(param => {
            dispatch(`parameters/${param}/fetch`, null, { root: true })
          })
          dispatch('zones/current', { id: null }, { root: true })
          resolve(gridModel)
        } else {
          reject(new Error('Selected grid model must be valid.'))
        }
      })
    },
    fetch: ({ commit }) => {
      return rms.gridModels().then(result => {
        commit('AVAILABLE', result)
      })
    }
  },

  mutations: {
    CURRENT: (state, selectedGridModel) => {
      state.current = selectedGridModel
    },
    AVAILABLE: (state, gridModels) => {
      state.available = gridModels
    },
  },

  getters: {},
}
