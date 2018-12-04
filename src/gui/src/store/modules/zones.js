import Vue from 'vue'

import { promiseSimpleCommit } from '@/store/utils'
import { Zone } from '@/store/utils/domain'
import { SELECTED_ITEMS } from '@/store/mutations'
import rms from '@/api/rms'
import { makeData, isEmpty, notEmpty } from '@/utils'

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
  },

  actions: {
    select: ({ commit, dispatch, state, rootState }, selected) => {
      const ids = selected.map(zone => zone.id)
      for (const id in state.available) {
        // TODO: Make sure all regions are also selected, of regions is in use (and this zone has regions)
        // FIXME: Ensure that 'intermediate' is preserved
        const toggled = ids.indexOf(id) >= 0
        if (rootState.regions.use) {
          // When a zone is (un)toggled, all of its regions should be (un)toggled
          const zone = state.available[`${id}`]
          Object.keys(state.available[`${zone.id}`].regions)
            .forEach(regionId => {
              commit('REGION_SELECTED', { zoneId: id, regionId, toggled })
              if (!toggled && regionId === rootState.regions.current) {
                dispatch('regions/current', { id: null }, { root: true })
              }
            })
        }
        commit('SELECTED', { id, toggled })
      }
      return Promise.resolve(ids)
    },
    current: ({ commit }, { id }) => {
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    fetch: ({ dispatch, rootGetters }) => {
      return rms.zones(rootGetters.gridModel)
        .then(zones => dispatch('populate', { zones }))
    },
    populate: ({ commit, dispatch, rootGetters }, { zones }) => {
      return new Promise((resolve, reject) => {
        const data = makeData(zones, Zone)
        commit('AVAILABLE', data)
        resolve(data)
      })
    },
    update ({ commit, dispatch, state }, { zones, zoneId, regions }) {
      if (isEmpty(zones) && notEmpty(regions)) {
        // We are setting/updating the regions for `zone`
        if (isEmpty(zoneId)) zoneId = state.current
        commit('REGIONS', { zoneId, regions })
        // TODO: Add new GRFs for each region if necessary
        // All regions selected
        if (Object.values(regions).every(region => region.selected)) commit('SELECTED', { id: zoneId, toggled: true })
        // Some region(s) selected
        else if (Object.values(regions).some(region => region.selected)) commit('SELECTED', { id: zoneId, toggled: 'intermediate' })
        // No regions selected
        else commit('SELECTED', { id: zoneId, toggled: false })
      } else {
        // TODO?
      }
    },
  },

  mutations: {
    AVAILABLE: (state, zones) => {
      Vue.set(state, 'available', zones)
    },
    SELECTED: SELECTED_ITEMS,
    CURRENT: (state, { id }) => {
      Vue.set(state, 'current', id)
    },
    REGIONS: (state, { zoneId, regions }) => {
      Vue.set(state.available[`${zoneId}`], 'regions', regions)
    },
    REGION_SELECTED: (state, { zoneId, regionId, toggled }) => {
      Vue.set(state.available[`${zoneId}`].regions[`${regionId}`], 'selected', toggled)
    },
  },

  getters: {
    selected (state) {
      return Object.keys(state.available).filter(id => state.available[`${id}`].selected)
    }
  },
}
