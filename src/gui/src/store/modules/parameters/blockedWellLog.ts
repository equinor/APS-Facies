import rms from '@/api/rms'
import { fetchParameterHelper } from '@/store/utils'
import { removeFaciesDependent } from '@/store/utils/helpers'

import { Module } from 'vuex'
import { SelectableChoice } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

const module: Module<SelectableChoice<string>, RootState> = {
  namespaced: true,

  state: {
    available: [],
    selected: null,
  },

  actions: {
    select: async (context, blockedWellLog): Promise<void> => {
      const { commit, dispatch } = context
      commit('CURRENT', blockedWellLog)
      await removeFaciesDependent(context)
      await dispatch('facies/global/fetch', null, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }): Promise<void> => {
      commit('CURRENT', null)
      await fetchParameterHelper({ commit, dispatch }, rms.blockedWellLogParameters(rootGetters.gridModel, rootGetters.blockedWellParameter))
    },
  },

  mutations: {
    AVAILABLE: (state, blockedWellLogs): void => {
      state.available = blockedWellLogs
    },
    CURRENT: (state, blockedWellLog): void => {
      state.selected = blockedWellLog
    },
  },

  getters: {},
}

export default module