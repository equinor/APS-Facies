import api from '@/api/rms'

import simBox from './simBox'

import { Module } from 'vuex'
import GridParameterState from '@/store/modules/parameters/grid/typing'
import { RootState } from '@/store/typing'

const module: Module<GridParameterState, RootState> = {
  namespaced: true,

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
    async fetch ({ commit, dispatch, rootGetters }, rough: boolean = true): Promise<void> {
      commit('_WAITING', true)
      const [x, y, z] = await api.gridSize(rootGetters.gridModel)
      await dispatch('parameters/fmu/fetch', z, { root: true })
      const azimuth = await dispatch('simBox/fetch', rough)
      await dispatch('populate', { azimuth, size: { x, y, z } })
      commit('_WAITING', false)
    },
    populate ({ commit }, { azimuth, size }): void {
      commit('SIZE', size)
      commit('AZIMUTH', azimuth)
    },
    thickness ({ commit }, zoneName) {},
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
    settings: (state, getters, rootState, rootGetters) => {},
  },
}

export default module
