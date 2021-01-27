import rms from '@/api/rms'

import { Module } from 'vuex'
import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

const module: Module<Selectable<string>, RootState> = {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    fetch: async ({ dispatch }): Promise<void> => {
      await dispatch('select', await rms.currentWorkflowName())
    },
    select: async ({ commit }, workflowName): Promise<void> => {
      commit('CURRENT', workflowName)
    },
  },

  mutations: {
    CURRENT: (state, workflowName): void => {
      state.selected = workflowName
    },
  },

  getters: {},
}

export default module
