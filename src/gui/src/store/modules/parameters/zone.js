export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    select: ({ commit }, zone) => {
      commit('CURRENT', zone)
    },
  },

  mutations: {
    CURRENT: (state, zone) => {
      state.selected = zone
    },
  },

  getters: {},
}
