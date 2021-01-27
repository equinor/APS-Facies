import rms from '@/api/rms'
import { RootState } from '@/store/typing'
import { ActionContext } from 'vuex'

import ProjectNameState from './typing'

export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    fetch: async ({ dispatch }: ActionContext<ProjectNameState, RootState>): Promise<void> => {
      await dispatch('select', await rms.projectName())
    },
    select: ({ commit }: ActionContext<ProjectNameState, RootState>, name: string): void => {
      commit('CURRENT', name)
    },
  },

  mutations: {
    CURRENT: (state: ProjectNameState, modelName: string): void => {
      state.selected = modelName
    },
  },
}
