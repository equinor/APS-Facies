import rms from '@/api/rms'
import { fetchParameterHelper } from '@/store/utils'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ commit, dispatch }, blockedWellLog) => {
      commit('CURRENT', blockedWellLog)
      await dispatch('facies/global/fetch', null, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }) => {
      commit('CURRENT', null)
      await fetchParameterHelper({ commit, dispatch }, rms.blockedWellLogParameters(rootGetters.gridModel, rootGetters.blockedWellParameter))
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
