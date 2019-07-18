import { Module } from 'vuex'
import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

import { defaultColors } from '@/utils/domain/facies/helpers/colors'

const module: Module<StaticChoices<string>, RootState> = {
  namespaced: true,

  state: {
    available: [],
  },

  modules: {},

  actions: {
    fetch ({ commit }): void {
      commit('AVAILABLE', defaultColors)
    }
  },

  mutations: {
    AVAILABLE (state, value): void {
      state.available = value
    }
  },
}

export default module
