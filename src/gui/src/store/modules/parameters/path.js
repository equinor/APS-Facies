import rms from '@/api/rms'

export default {
  namespaced: true,
  state: {
    project: '',
  },
  actions: {
    async fetch ({ dispatch }) {
      const path = await rms.projectDirectory()
      await dispatch('select', path)
    },
    select ({ commit }, path) {
      commit('PROJECT', path)
    },
  },
  mutations: {
    PROJECT: (state, path) => {
      state.project = path
    }
  },
}
