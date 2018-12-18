export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    select: ({ commit }, workflowName) => {
      commit('CURRENT', workflowName)
    },
  },

  mutations: {
    CURRENT: (state, workflowName) => {
      state.selected = workflowName
    },
  },

  getters: {},
}
