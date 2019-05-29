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
    select: async ({ commit, dispatch, state, rootState }, selected) => {
      for (const zone of Object.values(state.available)) {
        // TODO: Make sure all regions are also selected, of regions is in use (and this zone has regions)
        // FIXME: Ensure that 'intermediate' is preserved
        const toggled = includes(selected, zone)
        if (rootState.regions.use) {
          // When a zone is (un)toggled, all of its regions should be (un)toggled
          Object.values(state.available[`${zone.id}`].regions)
            .forEach(async region => {
              commit('REGION_SELECTED', { region, toggled })
              if (!toggled && region.id === rootState.regions.current) {
                await dispatch('regions/current', { id: null }, { root: true })
              }
            })
        }
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
    update ({ commit }, { regions }) {
      const zones = regions.reduce((zones, region) => {
        if (!(zones.map(zone => zone.id).includes(region.zone.id))) {
          zones.push(region.zone)
        }
        return zones
      }, [])
      zones.forEach(zone => {
        // We are setting/updating the regions for `zone`
        // TODO: Add new GRFs for each region if necessary
        // All regions selected
        if (Object.values(zone.regions).every(region => region.selected)) commit('SELECTED', { zone, toggled: true })
        // Some region(s) selected
        else if (Object.values(zone.regions).some(region => region.selected)) commit('SELECTED', { zone, toggled: 'intermediate' })
        // No regions selected
        else commit('SELECTED', { zone, toggled: false })
      })
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
    ADD_REGION: (state, { region }) => {
      Vue.set(state.available[`${region.zone.id}`]._regions, region.id, region)
    },
    REGIONS: (state, { zone, regions }) => {
      Vue.set(state.available[`${zone.id}`], '_regions', regions)
    },
    REGION_SELECTED: (state, { region, toggled }) => {
      Vue.set(state.available[`${region.zone.id}`]._regions[`${region.id}`], 'selected', toggled)
    },
  },

  getters: {
    selected (state) {
      return Object.keys(state.available).filter(id => state.available[`${id}`].selected)
    }
  },
}
