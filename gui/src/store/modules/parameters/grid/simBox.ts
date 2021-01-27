import api from '@/api/rms'

import { Module } from 'vuex'
import { SimulationBoxState } from '@/store/modules/parameters/grid/typing'
import { RootState } from '@/store/typing'

const module: Module<SimulationBoxState, RootState> = {
  namespaced: true,

  state: {
    size: {
      x: null, y: null, z: null,
    },
    origin: {
      x: null, y: null,
    },
  },

  actions: {
    async fetch ({ dispatch, rootGetters }, rough = false): Promise<number> {
      const simBox = await api.simulationBoxOrigin(rootGetters.gridModel, rough)
      await dispatch('populate', simBox)
      return simBox.rotation
    },
    populate ({ commit }, { size, origin }): void {
      commit('SIZE', size)
      commit('ORIGIN', origin)
    },
  },

  mutations: {
    SIZE: (state, { x, y, z }): void => {
      state.size.x = x
      state.size.y = y
      state.size.z = z
    },
    ORIGIN: (state, { x, y }): void => {
      state.origin.x = x
      state.origin.y = y
    },
  },
}

export default module
