import { promiseSimpleCommit, fetchParameterHelper } from 'Store/utils'
import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({commit, dispatch}, regionParameter) => {
      return promiseSimpleCommit(commit, 'CURRENT', regionParameter)
        .then(() => dispatch('regions/fetch', null, { root: true }))
    },
    fetch: ({commit, dispatch, rootGetters}) => {
      return fetchParameterHelper(commit, dispatch, rms.regionParameters(rootGetters.gridModel))
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
