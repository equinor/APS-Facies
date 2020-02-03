import GridModel from '@/utils/domain/gridModel'
import { Optional } from '@/utils/typing'

import simBox from './simBox'

import { Module } from 'vuex'
import GridParameterState from '@/store/modules/parameters/grid/typing'
import { RootState } from '@/store/typing'

const module: Module<GridParameterState, RootState> = {
  namespaced: true,

  // eslint-disable-next-line @typescript-eslint/ban-ts-ignore
  // @ts-ignore
  state: {
    _waiting: false,
    azimuth: null,
    size: {
      x: null, y: null, z: null,
    }
  },

  modules: {
    simBox,
  },

  actions: {
    async fetch ({ commit, dispatch, rootGetters }, rough = true): Promise<void> {
      commit('_WAITING', true)
      const grid: Optional<GridModel> = rootGetters['gridModels/current']
      if (grid) {
        await dispatch('fmu/maxDepth/fetch', undefined, { root: true })
        const azimuth = await dispatch('simBox/fetch', rough)
        await dispatch('populate', { azimuth, size: grid.dimension })
      }
      commit('_WAITING', false)
    },
    async refresh (): Promise<void> { /* Stub */ },
    populate ({ commit }, { azimuth, size }): void {
      commit('SIZE', size)
      commit('AZIMUTH', azimuth)
    },
  },
  mutations: {
    SIZE: (state, { x, y, z }): void => {
      state.size.x = x
      state.size.y = y
      state.size.z = z
    },
    AZIMUTH: (state, azimuth): void => {
      state.azimuth = azimuth
    },
    _WAITING: (state, waiting): void => {
      state._waiting = waiting
    },
  },
  getters: {
    waiting: (state): boolean => {
      return state._waiting
    },
  },
}

export default module
