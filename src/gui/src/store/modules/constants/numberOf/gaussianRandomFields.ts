import { MinMaxState, NumberOfGaussianRandomFieldsState } from '@/store/modules/constants/typing'
import { RootState } from '@/store/typing'
import { Bayfill } from '@/utils/domain/truncationRule'
import { Optional } from '@/utils/typing'
import { Module } from 'vuex'

const defaultMinimum = 2
const numberBayfill = 3

const numbers = (min: number, max: number): Module<MinMaxState, RootState> => {
  return {
    namespaced: true,

    state (): MinMaxState {
      return {
        min: 0,
        max: 0,
      }
    },

    actions: {
      async fetch ({ commit }): Promise<void> {
        commit('MINIMUM', min)
        commit('MAXIMUM', max)
      },
    },

    mutations: {
      MINIMUM (state, value): void {
        state.min = value
      },
      MAXIMUM (state, value): void {
        state.max = value
      },
    },
  }
}

const module: Module<NumberOfGaussianRandomFieldsState, RootState> = {
  namespaced: true,

  modules: {
    cubic: numbers(defaultMinimum, Number.POSITIVE_INFINITY),
    nonCubic: numbers(defaultMinimum, Number.POSITIVE_INFINITY),
    bayfill: numbers(numberBayfill, numberBayfill),
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await Promise.all([
        dispatch('cubic/fetch'),
        dispatch('nonCubic/fetch'),
        dispatch('bayfill/fetch'),
      ])
    },
  },

  getters: {
    // CURRENT
    minimum (state, getters, rootState, rootGetters): Optional<number> {
      if (rootGetters.truncationRule instanceof Bayfill) {
        return state.bayfill.min
      } else {
        return defaultMinimum
      }
    }
  },
}

export default module
