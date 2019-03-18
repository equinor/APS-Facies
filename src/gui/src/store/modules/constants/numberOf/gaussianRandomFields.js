import { Bayfill } from '@/utils/domain/truncationRule'

const defaultMinimum = 2
const numberBayfill = 3

const numbers = (min, max) => {
  return {
    namespaced: true,

    state () {
      return {
        min: null,
        max: null,
      }
    },

    actions: {
      fetch ({ commit }) {
        commit('MINIMUM', min)
        commit('MAXIMUM', max)
      },
    },

    mutations: {
      MINIMUM (state, value) {
        state.min = value
      },
      MAXIMUM (state, value) {
        state.max = value
      },
    },
  }
}

export default {
  namespaced: true,

  modules: {
    cubic: numbers(defaultMinimum, Number.POSITIVE_INFINITY),
    nonCubic: numbers(defaultMinimum, Number.POSITIVE_INFINITY),
    bayfill: numbers(numberBayfill, numberBayfill),
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('cubic/fetch')
      dispatch('nonCubic/fetch')
      dispatch('bayfill/fetch')
    },
  },

  getters: {
    // CURRENT
    minimum (state, getters, rootState, rootGetters) {
      const type = rootGetters.truncationRule
        ? typeof rootGetters.truncationRule
        : null
      if (type === Bayfill) {
        return state.bayfill.min
      } else {
        return defaultMinimum
      }
    }
  },
}
