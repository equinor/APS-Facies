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
      blockedWellLog = blockedWellLog || null
      commit('CURRENT', blockedWellLog)
      await removeFaciesDependent(context)
      if (blockedWellLog) {
        await dispatch('facies/global/fetch', null, { root: true })
        await dispatch('facies/selectObserved', undefined, { root: true })
      } else {
        await dispatch('facies/global/reset', undefined, { root: true })
      }
    },
    fetch: async (context): Promise<void> => {
      await fetchParameterHelper(context)
    },
    refresh: async ({ commit, rootGetters }): Promise<void> => {
      const { gridModel, blockedWellParameter } = rootGetters
      commit('AVAILABLE', gridModel && blockedWellParameter
        ? await rms.blockedWellLogParameters(gridModel, blockedWellParameter)
        : []
      )
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
