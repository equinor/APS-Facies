import { Module } from 'vuex'
import { RootState } from '@/store/typing'

import ranges from './ranges'
import options from './options'
import faciesColors from './faciesColors'
import numberOf from './numberOf'

const module: Module<Record<string, unknown>, RootState> = {
  namespaced: true,

  modules: {
    ranges,
    options,
    faciesColors,
    numberOf,
  },

  actions: {
    async fetch ({ dispatch }): Promise<void> {
      // Ranged values (min/max)
      await Promise.all([
        dispatch('ranges/fetch'),

        // Get available options
        dispatch('options/fetch'),

        // Get the standard colors for facies
        dispatch('faciesColors/fetch'),

        // Get minimum, and maximum number of fields for different truncation rules
        dispatch('numberOf/fetch'),
      ])
    }
  },
}

export default module
