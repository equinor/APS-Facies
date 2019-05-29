import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    selected: null,
  },

  actions: {
    fetch: async ({ dispatch }) => {
      dispatch('select', await rms.currentWorkflowName())
    },
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
