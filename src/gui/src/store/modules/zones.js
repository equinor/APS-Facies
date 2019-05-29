import Vue from 'vue'

import { Zone } from '@/utils/domain'
import rms from '@/api/rms'
import Region from '@/utils/domain/region'
import { identify, includes } from '@/utils/helpers'

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
  },

  actions: {
    select: async ({ commit, state }, selected) => {
      for (const zone of Object.values(state.available)) {
        const toggled = includes(selected, zone)
        commit('SELECTED', { zone, toggled })
      }
    },
    current: async ({ commit, dispatch, state }, { id }) => {
      await dispatch('truncationRules/resetTemplate', { type: '', template: '' }, { root: true })
      await dispatch('gaussianRandomFields/crossSections/fetch', { zone: id }, { root: true })
      commit('CURRENT', { id })

      const zone = state.available[`${id}`]
      await dispatch('parameters/grid/thickness', zone.name, { root: true })
      await dispatch('parameters/grid/simBox/thickness', zone.name, { root: true })
    },
    fetch: async ({ dispatch, rootGetters }) => {
      await dispatch('populate', { zones: await rms.zones(rootGetters.gridModel) })
    },
    populate: async ({ commit }, { zones }) => {
      zones.forEach(zone => {
        if ('regions' in zone && Array.isArray(zone.regions)) {
          zone.regions = zone.regions.map(region => new Region(region))
        }
      })
      zones = zones.map(zone => new Zone(zone))
      zones.forEach(zone => { zone.regions.forEach(region => { region.zone = zone }) })
      commit('AVAILABLE', identify(zones))
      return zones
    },
  },

  mutations: {
    AVAILABLE: (state, zones) => {
      Vue.set(state, 'available', zones)
    },
    SELECTED: (state, { zone, toggled }) => {
      Vue.set(state.available[`${zone.id}`], 'selected', toggled)
    },
    CURRENT: (state, { id }) => {
      Vue.set(state, 'current', id)
    },
  },

  getters: {
    selected (state) {
      return Object.keys(state.available).filter(id => state.available[`${id}`].selected)
    }
  },
}
