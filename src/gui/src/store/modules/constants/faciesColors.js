import { defaultColors } from '@/utils/domain/facies/helpers/colors'

export default {
  namespaced: true,

  state: {
    available: [],
  },

  modules: {},

  actions: {
    fetch ({ commit }) {
      commit('AVAILABLE', defaultColors)
    }
  },

  mutations: {
    AVAILABLE (state, value) {
      state.available = value
    }
  },

  getters: {},
}
