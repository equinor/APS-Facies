import Vue from 'vue'

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
          const parameters = ['region', 'blockedWell', 'rmsTrend', 'probabilityCube']
          // when loading a file, we must ensure that all promises in this method are resolved before calling the
          // next method in the loading chain. The loading chain depends on the fetch statements in this methods being
          // resolved.
          const promises = []
          parameters.forEach(param => {
            promises.push(dispatch(`parameters/${param}/fetch`, null, { root: true }))
          })
          promises.push(dispatch('zones/fetch', null, { root: true }))
          Promise.all(promises)
            .then(() => {
              resolve(gridModel)
            })
            .catch(error => {
              reject(error)
            })
        } else {
          let errorMsg = `Selected grid model ( ${gridModel} ) is not present in the current project.\n\n `
          errorMsg += `Tip: GridModelName in the APS model file must be one of { ${state.available.join()} } `
          reject(new Error(errorMsg))
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
      Vue.set(state, 'current', selectedGridModel)
    },
    AVAILABLE: (state, gridModels) => {
      state.available = gridModels
    },
  },

  getters: {},
}
