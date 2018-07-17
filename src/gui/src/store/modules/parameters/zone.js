import { promiseSimpleCommit } from '@/store/utils'
import rms from '@/api/rms'

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
      return rms.zoneParameters(rootGetters.gridModel)
        .then(result => {
          commit('AVAILABLE', result)
          if (result.length === 1) {
            dispatch('select', result[0])
          }
        })
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
