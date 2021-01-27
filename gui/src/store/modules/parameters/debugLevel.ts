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
      if (level >= 0 && level <= 4) {
        commit('SET', level)
      } else {
        throw Error(`The debug level MUST be between 0, and 4. (was ${level})`)
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
