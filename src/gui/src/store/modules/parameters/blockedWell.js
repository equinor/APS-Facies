import { promiseSimpleCommit, fetchParameterHelper } from 'Store/utils'
import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({commit, dispatch}, blockedWell) => {
      return promiseSimpleCommit(commit, 'CURRENT', blockedWell)
        .then(() => { dispatch('parameters/blockedWellLog/fetch', null, { root: true }) })
    },
    fetch: ({commit, dispatch, rootGetters}) => {
      return fetchParameterHelper(commit, dispatch, rms.blockedWellParameters(rootGetters.gridModel))
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
