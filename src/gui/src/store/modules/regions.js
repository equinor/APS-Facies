import Vue from 'vue'
import { Region } from '@/utils/domain'
import { makeData, isEmpty, notEmpty, includes } from '@/utils'
import rms from '@/api/rms'

async function fetchRegions ({ rootGetters, commit }, zone) {
  (await rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter))
    .forEach(region => {
      const exists = zone.regions.find(({ code, name }) => region.code === code && region.name === name)
      if (!exists) {
        commit('ADD', new Region({
          ...region,
          selected: !!zone.selected,
          zone,
        }))
      }
    })
}

export default {
  namespaced: true,

  state: {
    current: null,
    use: false,
    _loading: false,
  },

  modules: {},

  actions: {
    select: async ({ commit, rootGetters }, regions) => {
      const affectedZones = regions.reduce((unique, region) => {
        if (!(includes(unique, region.zone))) {
          unique.push(region.zone)
        }
        return unique
      }, [])
      for (const zone of affectedZones) {
        zone.regions.forEach(region => {
          commit('TOGGLE', { region, toggled: includes(regions, region) })
        })
      }
      if (regions.length === 0) {
        // All regions of, presumably, the current zone has been deselected
        commit('zones/SELECTED', { toggled: false, zone: rootGetters.zone }, { root: true })
      }
    },
    current: async ({ commit, dispatch, rootState }, { id }) => {
      const zone = Object.values(rootState.zones.available)
        .find(zone => Object.values(zone.regions).map(region => region.id).includes(id))
      await dispatch('gaussianRandomFields/crossSections/fetch', { zone, region: id }, { root: true })
      commit('CURRENT', { id })
      await dispatch('truncationRules/preset/fetch', undefined, { root: true })
    },
    fetch: async ({ commit, rootState, rootGetters, state }, zone) => {
      // TODO: Add new GRFs for each region if necessary
      if (state.use && notEmpty(rootGetters.regionParameter)) {
        commit('LOADING', true)
        if (isEmpty(zone)) {
          for (const zone of Object.values(rootState.zones.available)) {
            await fetchRegions({ commit, rootGetters }, zone)
          }
        } else {
          await fetchRegions({ commit, rootGetters }, zone)
        }
        commit('LOADING', false)
      }
    },
    use: async ({ commit, dispatch }, { use, fetch = true }) => {
      commit('USE', use)
      commit('CURRENT', { id: null })
      if (fetch) {
        await dispatch('fetch', null)
      }
    },
    populate: async ({ commit, dispatch, state }, regions) => {
      regions = makeData(regions, Region, state.available)
      commit('AVAILABLE', { regions })
      await dispatch('select', { regions: Object.values(regions).filter(({ selected }) => !!selected) })
    },
  },

  mutations: {
    ADD: (state, region) => {
      Vue.set(region.zone._regions, region.id, region)
    },
    TOGGLE: (state, { region, toggled }) => {
      Vue.set(region.zone._regions[`${region.id}`], 'selected', toggled)
    },
    AVAILABLE: (state, { regions }) => {
      Vue.set(state, 'available', regions)
    },
    CURRENT: (state, { id }) => {
      Vue.set(state, 'current', id)
    },
    USE: (state, value) => {
      Vue.set(state, 'use', value)
    },
    LOADING: (state, toggle) => {
      Vue.set(state, '_loading', toggle)
    },
  },

  getters: {},
}
