import { promiseSimpleCommit } from '@/store/utils'
import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  modules: {},

  actions: {
    select: ({commit, dispatch}, regionParameter) => {
      return promiseSimpleCommit(commit, 'CURRENT', regionParameter)
        .then(() => dispatch('regions/fetch', null, { root: true }))
    },
    fetch: ({commit, rootGetters}) => {
      return rms.regionParameters(rootGetters.gridModel)
        .then(result => {
          commit('AVAILABLE', result)
        })
    },
  },

  mutations: {
    AVAILABLE: (state, regionParameters) => {
      state.available = regionParameters
    },
    CURRENT: (state, regionParameter) => {
      state.selected = regionParameter
    },
  },

  getters: {},
}
