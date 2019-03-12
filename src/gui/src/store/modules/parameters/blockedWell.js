import rms from '@/api/rms'
import { fetchParameterHelper } from '@/store/utils'

export default {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async ({ commit, dispatch }, blockedWell) => {
      commit('CURRENT', blockedWell)
      await dispatch('parameters/blockedWellLog/fetch', null, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }) => {
      commit('CURRENT', null)
      await fetchParameterHelper({ commit, dispatch }, rms.blockedWellParameters(rootGetters.gridModel))
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
