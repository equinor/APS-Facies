import rms from '@/api/rms'

export const selectable = {
  namespaced: true,

  state () {
    return {
      available: [],
    }
  },

  actions: {
    fetch ({ commit }, type) {
      return rms.options(type)
        .then(types => {
          commit('AVAILABLE', types)
        })
    }
  },

  mutations: {
    AVAILABLE (store, types) {
      store.available = types
    }
  },
}

export default {
  namespaced: true,

  modules: {
    variograms: selectable,
    origin: selectable,
    stacking: selectable,
    trends: selectable,
  },

  actions: {
    fetch ({ dispatch }) {
      return Promise.all([
        dispatch('variograms/fetch', 'variogram'),
        dispatch('origin/fetch', 'origin'),
        dispatch('stacking/fetch', 'stacking_direction'),
        dispatch('trends/fetch', 'trend'),
      ])
    }
  },
}
