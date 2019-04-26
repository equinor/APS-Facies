import gaussianRandomFields from './gaussianRandomFields'

export default {
  namespaced: true,

  state: {},

  modules: {
    gaussianRandomFields,
  },

  actions: {
    async fetch ({ dispatch }) {
      await dispatch('gaussianRandomFields/fetch')
    }
  },

  mutations: {},

  getters: {},
}
