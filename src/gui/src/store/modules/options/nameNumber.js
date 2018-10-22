const item = {
  namespaced: true,
  state: () => {
    return {
      show: 'number',
      legal: ['number', 'name']
    }
  },
  actions: {
    set: ({ commit, state }, value) => {
      if (state.legal.indexOf(value) >= 0) {
        commit('SET', value)
      }
    },
  },
  mutations: {
    SET: (state, value) => {
      state.show = value
    },
  },
  getters: {},
}

export default {
  namespaced: true,
  state: {
  },
  modules: {
    zone: item,
    region: item,
  },
  actions: {},
  mutations: {},
  getters: {},
}
