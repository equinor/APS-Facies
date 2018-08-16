import { promiseSimpleCommit, fetchParameterHelper } from 'Store/utils'
import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({commit, dispatch}, zoneParameter) => {
      return promiseSimpleCommit(commit, 'CURRENT', zoneParameter)
        .then(() => dispatch('zones/fetch', null, { root: true }))
    },
    fetch: ({commit, dispatch, rootGetters}) => {
      return fetchParameterHelper(commit, dispatch, rms.zoneParameters(rootGetters.gridModel))
    },
  },

  mutations: {
    AVAILABLE: (state, zoneParameters) => {
      state.available = zoneParameters
    },
    CURRENT: (state, zoneParameter) => {
      state.selected = zoneParameter
    },
  },

  getters: {},
}
