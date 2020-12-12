import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

const module: Module<Selectable<number>, RootState> = {
  namespaced: true,

  state: {
    selected: 0,
  },

  actions: {
    async select ({ commit }, level: number): Promise<void> {
      if (level >= 0 && level <= 1) {
        commit('SET', level)
      } else {
        throw Error(`The transform type MUST be between 0, and 1. (was ${level})`)
      }
    },
  },

  mutations: {
    SET (state, level: number): void {
      state.selected = level
    }
  }
}

export default module
