import { promiseSimpleCommit } from '@/store/utils'
import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: [],
    current: null,
  },

  actions: {
    select: ({commit}, zones) => {
      return promiseSimpleCommit(commit, 'CURRENT', zones)
    },
    current: ({commit}, zone) => {
      // TODO: Dispatch action to determine which regions are available
      return promiseSimpleCommit(commit, 'CURRENT', zone)
    },
    fetch: ({commit, state, rootGetters}) => {
      return rms.zones(rootGetters.gridModel, rootGetters.zoneParameter)
        .then(zones => {
          commit('AVAILABLE', zones)
        })
    },
  },

  mutations: {
    AVAILABLE: (state, zones) => {
      state.available = zones
    },
    SELECTED: (state, selectedZones) => {
      state.selected = selectedZones
    },
    CURRENT: (state, currentZone) => {
      state.current = currentZone
    },
  },

  getters: {},
}
