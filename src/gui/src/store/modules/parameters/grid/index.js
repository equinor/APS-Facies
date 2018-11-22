import api from '@/api/rms'

import simBox from './simBox'

export default {
  namespaced: true,
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
    async fetch ({ commit, dispatch, rootGetters }) {
      commit('_WAITING', true)
      const [x, y, z] = await api.gridSize(rootGetters.gridModel)
      const azimuth = await dispatch('simBox/fetch')
      commit('_WAITING', false)

      commit('SIZE', { x, y, z })
      commit('AZIMUTH', azimuth)
    },
    thickness ({ commit }, zoneName) {},
  },
  mutations: {
    SIZE: (state, { x, y, z }) => {
      state.size.x = x
      state.size.y = y
      state.size.z = z
    },
    AZIMUTH: (state, azimuth) => {
      state.azimuth = azimuth
    },
    _WAITING: (state, waiting) => {
      state._waiting = waiting
    },
  },
  getters: {
    waiting: (state) => {
      return state._waiting
    },
    settings: (state, getters, rootState, rootGetters) => {},
  },
}
