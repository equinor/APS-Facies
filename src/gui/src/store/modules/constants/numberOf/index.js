import gaussianRandomFields from './gaussianRandomFields'

export default {
  namespaced: true,

  state: {},

  modules: {
    gaussianRandomFields,
  },

  actions: {
    fetch ({ dispatch }) {
      dispatch('gaussianRandomFields/fetch')
    }
  },

  mutations: {},

  getters: {},
}
