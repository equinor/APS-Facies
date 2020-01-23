import rms from '@/api/rms'
import { fetchParameterHelper } from '@/store/utils'

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
    select: async ({ commit, dispatch }, blockedWell): Promise<void> => {
      commit('CURRENT', blockedWell)
      await dispatch('parameters/blockedWellLog/select', null, { root: true })
      await dispatch('parameters/blockedWellLog/fetch', null, { root: true })
    },
    fetch: async (context): Promise<void> => {
      await fetchParameterHelper(context)
    },
    refresh: async ({ commit, rootGetters }): Promise<void> => {
      commit('AVAILABLE', await rms.blockedWellParameters(rootGetters.gridModel))
    },
  },

  mutations: {
    AVAILABLE: (state, blockedWells): void => {
      state.available = blockedWells
    },
    CURRENT: (state, blockedWell): void => {
      state.selected = blockedWell
    },
  },
}

export default module
