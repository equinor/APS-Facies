import { promiseSimpleCommit, fetchParameterHelper } from 'Store/utils'
import rms from 'Api/rms'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: ({commit, dispatch}, blockedWellLog) => {
      return promiseSimpleCommit(commit, 'CURRENT', blockedWellLog)
        .then(() => { dispatch('facies/fetch', null, { root: true }) })
    },
    fetch: ({commit, dispatch, rootGetters}) => {
      return fetchParameterHelper(commit, dispatch, rms.blockedWellLogParameters(rootGetters.gridModel, rootGetters.blockedWellParameter))
    },
  },

  mutations: {
    AVAILABLE: (state, blockedWellLogs) => {
      state.available = blockedWellLogs
    },
    CURRENT: (state, blockedWellLog) => {
      state.selected = blockedWellLog
    },
  },

  getters: {},
}
