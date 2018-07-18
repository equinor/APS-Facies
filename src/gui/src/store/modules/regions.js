import { promiseSimpleCommit } from 'Store/utils'
import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: [],
    current: null,
  },

  modules: {},

  actions: {
    select: ({commit}, regions) => {
      return promiseSimpleCommit(commit, 'SELECTED', regions)
    },
    current: ({commit}, region) => {
      return promiseSimpleCommit(commit, 'CURRENT', region)
    },
    fetch: ({commit, rootGetters}) => {
      return rms.regions(rootGetters.gridModel, rootGetters.zone.name, rootGetters.regionParameter)
        .then(regions => {
          commit('AVAILABLE', regions)
        })
    },
  },

  mutations: {
    AVAILABLE: (state, regions) => {
      state.available = regions
    },
    SELECTED: (state, regions) => {
      state.selected = regions
    },
    CURRENT: (state, region) => {
      state.current = region
    },
  },

  getters: {},
}
