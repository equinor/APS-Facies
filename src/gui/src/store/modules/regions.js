import Vue from 'vue'
import { promiseSimpleCommit } from '@/store/utils'
import { Region } from '@/utils/domain'
import { makeData, isEmpty, notEmpty, includes } from '@/utils'
import rms from '@/api/rms'

export default {
  namespaced: true,

  state: {
    current: null,
    use: false,
  },

  modules: {},

  actions: {
    select: async ({ dispatch, commit }, regions) => {
      regions.forEach(({ zone }) => {
        zone.regions.forEach(region => {
          commit('TOGGLE', { region, toggled: includes(regions, region) })
        })
      })
      await dispatch('zones/update', { regions }, { root: true })
    },
    current: async ({ commit, dispatch, rootState }, { id }) => {
      const zone = Object.values(rootState.zones.available)
        .find(zone => Object.values(zone.regions).map(region => region.id).includes(id))
      await dispatch('truncationRules/resetTemplate', { type: '', template: '' }, { root: true })
      await dispatch('gaussianRandomFields/crossSections/fetch', { zone, region: id }, { root: true })
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    fetch: async ({ commit, rootState, rootGetters, state }, zoneId) => {
      if (state.use && notEmpty(rootGetters.regionParameter)) {
        if (isEmpty(zoneId)) {
          for (const zone of Object.values(rootState.zones.available)) {
            (await rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter))
              .forEach(region => {
                // TODO: Don't add if one exists with the same code / name
                commit('ADD', new Region({
                  ...region,
                  selected: !!zone.selected,
                  zone,
                }))
              })
          }
        } else {
          // TODO
        }
      }
      return Promise.resolve(
        zoneId
          ? rootState.zones.available[`${zoneId}`].regions
          : []
      )
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
  },

  getters: {},
}
