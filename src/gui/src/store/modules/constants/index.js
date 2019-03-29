import ranges from './ranges'
import options from './options'
import faciesColors from './faciesColors'
import numberOf from './numberOf'

export default {
  namespaced: true,

  state: {},

  modules: {
    ranges,
    options,
    faciesColors,
    numberOf,
  },

  actions: {
    fetch ({ dispatch }) {
      // Ranged values (min/max)
      return Promise.all([
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

  mutations: {},

  getters: {},
}
