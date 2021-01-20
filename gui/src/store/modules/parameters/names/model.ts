import { Module } from 'vuex'

import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

const module: Module<Selectable<string>, RootState> = {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    select: ({ commit }, modelName): void => {
      commit('CURRENT', modelName)
    },
  },

  mutations: {
    CURRENT: (state, modelName): void => {
      state.selected = modelName
    },
  },

  getters: {},
}

export default module
