import rms from '@/api/rms'

export const ranged = {
  namespaced: true,

  state () {
    return {
      min: null,
      max: null,
    }
  },

  actions: {
    fetch ({commit}, type) {
      rms.constants(type, 'min,max')
        .then(res => {
          commit('MAXIMUM', res.max)
          commit('MINIMUM', res.min)
        })
    },
  },

  mutations: {
    MINIMUM (state, value) {
      state.min = value
    },
    MAXIMUM (state, value) {
      state.max = value
    },
  },
}

export default {
  namespaced: true,

  modules: {
    azimuth: ranged,
    dip: ranged,
    power: ranged,
    depositionalAzimuth: ranged,
    stacking: ranged,
    migration: ranged,
  },

  actions: {
    fetch ({dispatch}) {
      dispatch('azimuth/fetch', 'azimuth')
      dispatch('dip/fetch', 'dip')
      dispatch('power/fetch', 'power')
      dispatch('depositionalAzimuth/fetch', 'depositional_direction')
      dispatch('stacking/fetch', 'stacking_angle')
      dispatch('migration/fetch', 'migration_angle')
    }
  },
}
