import ranges from './ranges'
import options from './options'
import faciesColors from './faciesColors'

export default {
  namespaced: true,

  state: {},

  modules: {
    ranges,
    options,
    faciesColors,
  },

  actions: {
    fetch ({ dispatch }) {
      // Ranged values (min/max)
      dispatch('ranges/fetch')

      // Get available options
      dispatch('options/fetch')

      // Get the standard colors for facies
      dispatch('faciesColors/fetch')
    }
  },

  mutations: {},

  getters: {},
}
