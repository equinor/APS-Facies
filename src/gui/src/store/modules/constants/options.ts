import { Module } from 'vuex'
import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'

import rms from '@/api/rms'

export const selectable: Module<StaticChoices<string>, RootState> = {
  namespaced: true,

  state (): StaticChoices<string> {
    return {
      available: [],
    }
  },

  actions: {
    async fetch ({ commit }, type: string): Promise<void> {
      const types = await rms.options(type)
      commit('AVAILABLE', types)
    }
  },

  mutations: {
    AVAILABLE (store, types: string[]): void {
      store.available = types
    }
  },
}

const module: Module<{}, RootState> = {
  namespaced: true,

  modules: {
    variograms: selectable,
    origin: selectable,
    stacking: selectable,
    trends: selectable,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await Promise.all([
        dispatch('variograms/fetch', 'variogram'),
        dispatch('origin/fetch', 'origin'),
        dispatch('stacking/fetch', 'stacking_direction'),
        dispatch('trends/fetch', 'trend'),
      ])
    }
  },
}

export default module
