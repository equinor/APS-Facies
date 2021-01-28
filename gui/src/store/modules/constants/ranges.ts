import { MinMaxState } from '@/store/modules/constants/typing'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

import rms from '@/api/rms'

export const ranged: Module<MinMaxState, RootState> = {
  namespaced: true,

  state (): MinMaxState {
    return {
      min: null,
      max: null,
    }
  },

  actions: {
    async fetch ({ commit }, type): Promise<void> {
      const { min, max } = await rms.constants(type, 'min,max')
      commit('MAXIMUM', max)
      commit('MINIMUM', min)
    },
  },

  mutations: {
    MINIMUM (state, value: number): void {
      state.min = value
    },
    MAXIMUM (state, value: number): void {
      state.max = value
    },
  },
}

const module: Module<Record<string, unknown>, RootState> = {
  namespaced: true,

  modules: {
    azimuth: ranged,
    dip: ranged,
    power: ranged,
    depositionalAzimuth: ranged,
    stacking: ranged,
    migration: ranged,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await Promise.all([
        dispatch('azimuth/fetch', 'azimuth'),
        dispatch('dip/fetch', 'dip'),
        dispatch('power/fetch', 'power'),
        dispatch('depositionalAzimuth/fetch', 'depositional_direction'),
        dispatch('stacking/fetch', 'stacking_angle'),
        dispatch('migration/fetch', 'migration_angle'),
      ])
    }
  },
}

export default module
