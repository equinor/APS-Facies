export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    select: ({ commit }, modelName) => {
      commit('CURRENT', modelName)
    },
  },

  mutations: {
    CURRENT: (state, modelName) => {
      state.selected = modelName
    },
  },

  getters: {},
}
