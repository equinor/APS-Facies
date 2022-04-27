import rms from '@/api/rms'
import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { RootState } from '@/store/typing'
import { Module } from 'vuex'

export interface TrendMap {
  name: string
  representations: string[]
}

const module: Module<StaticChoices<TrendMap>, RootState> = {
  namespaced: true,

  state: {
    available: [],
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      await dispatch('refresh')
    },
    refresh: async ({ commit }): Promise<void> => {
      const params = await rms.trendMapZones()
      commit(
        'AVAILABLE',
        Object.entries(params)
          .map(([zone, representations]) => ({
            name: zone,
            representations,
          }))
      )
    },
  },

  mutations: {
    AVAILABLE (state, params): void {
      state.available = params
    },
  },
}

export default module
