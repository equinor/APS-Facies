import rms from '@/api/rms'
import { Selectable } from '@/store/modules/parameters/typing/helpers'
import { Module } from 'vuex'
import { RootState } from '@/store/typing'

const module: Module<Selectable<number>, RootState> = {
  namespaced: true,

  state: {
    selected: 0,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      const { tolerance } = await rms.constants('max_allowed_fraction_of_values_outside_tolerance', 'tolerance')
      await dispatch('select', tolerance)
    },

    async select ({ commit }, value: number): Promise<void> {
      commit('SET', value)
    }
  },

  mutations: {
    SET (state, value: number): void {
      state.selected = value
    },
  },
}

export default module
