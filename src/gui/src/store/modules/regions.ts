import Vue from 'vue'

import { Module } from 'vuex'
import { RegionState } from '@/store/modules/typing'
import { Context, RootState } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import Zone, { RegionConfiguration } from '@/utils/domain/zone'

import { Region } from '@/utils/domain'
import { makeData, isEmpty, notEmpty, includes } from '@/utils'
import rms from '@/api/rms'

async function fetchRegions ({ rootGetters, commit }: Context<RegionState, RootState>, zone: Zone): Promise<void> {
  (await rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter))
    .forEach((region: { code: number, name: string }): void => {
      const exists = zone.regions.find(({ code, name }): boolean => region.code === code && region.name === name)
      if (!exists) {
        commit('ADD', new Region({
          ...region,
          selected: !!zone.selected,
          zone,
        }))
      }
    })
}

const module: Module<RegionState, RootState> = {
  namespaced: true,

  state: {
    current: null,
    use: false,
    _loading: false,
  },

  actions: {
    select: async ({ commit, rootGetters }, regions: Region[]): Promise<void> => {
      const affectedZones = regions.reduce((unique, region): Zone[] => {
        if (!(includes(unique, region.zone))) {
          unique.push(region.zone)
        }
        return unique
      }, [] as Zone[])
      for (const zone of affectedZones) {
        zone.regions.forEach((region): void => {
          commit('TOGGLE', { region, toggled: includes(regions, region) })
        })
      }
      if (regions.length === 0) {
        // All regions of, presumably, the current zone has been deselected
        commit('zones/SELECTED', { toggled: false, zone: rootGetters.zone }, { root: true })
      }
    },
    current: async ({ commit, dispatch, rootState }, { id }): Promise<void> => {
      const zone = Object.values(rootState.zones.available)
        .find((zone): boolean => Object.values(zone.regions).map((region): ID => region.id).includes(id))
      await dispatch('gaussianRandomFields/crossSections/fetch', { zone, region: id }, { root: true })
      commit('CURRENT', { id })
      await dispatch('truncationRules/preset/fetch', undefined, { root: true })
    },
    fetch: async (context, zone): Promise<void> => {
      const { commit, rootState, rootGetters, state } = context
      // TODO: Add new GRFs for each region if necessary
      if (state.use && notEmpty(rootGetters.regionParameter)) {
        commit('LOADING', true)
        if (isEmpty(zone)) {
          for (const zone of Object.values(rootState.zones.available)) {
            commit('REMOVE_ALL', zone)
            await fetchRegions(context, zone)
          }
        } else {
          await fetchRegions(context, zone)
        }
        commit('LOADING', false)
      }
    },
    use: async ({ commit, dispatch }, { use, fetch = true }): Promise<void> => {
      commit('USE', use)
      commit('CURRENT', { id: null })
      if (fetch) {
        await dispatch('fetch', null)
      }
    },
    populate: async ({ commit, dispatch }, configurations: RegionConfiguration[]): Promise<void> => {
      const regions = makeData(configurations, Region)
      commit('AVAILABLE', { regions })
      await dispatch('select', { regions: Object.values(regions).filter(({ selected }): boolean => !!selected) })
    },
  },

  mutations: {
    ADD: (state, region): void => {
      Vue.set(region.zone._regions, region.id, region)
    },
    REMOVE_ALL: (state, zone): void => {
      Vue.set(zone, '_regions', {})
    },
    TOGGLE: (state, { region, toggled }): void => {
      Vue.set(region.zone._regions[`${region.id}`], 'selected', toggled)
    },
    AVAILABLE: (state, { regions }): void => {
      Vue.set(state, 'available', regions)
    },
    CURRENT: (state, { id }): void => {
      Vue.set(state, 'current', id)
    },
    USE: (state, value): void => {
      Vue.set(state, 'use', value)
    },
    LOADING: (state, toggle): void => {
      Vue.set(state, '_loading', toggle)
    },
  },
}

export default module
