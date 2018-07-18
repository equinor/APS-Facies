import ranges from './ranges'
import options from './options'

export default {
  namespaced: true,

  state: {},

  modules: {
    ranges,
    options,
  },

  actions: {
    fetch ({dispatch}) {
      // Ranged values (min/max)
      dispatch('ranges/fetch')

      // Get available options
      dispatch('options/fetch')
    }
  },

  mutations: {},

  getters: {},
}
