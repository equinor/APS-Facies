import { getId } from '@/utils'
import { Dependent } from '@/utils/domain/bases/interfaces'
import Vue from 'vue'

import { Module } from 'vuex'
import { ZoneState } from '@/store/modules/typing'
import { RootState } from '@/store/typing'
import APSError from '@/utils/domain/errors/base'
import { ID } from '@/utils/domain/types'
import { ZoneConfiguration } from '@/utils/domain/zone'
import { Optional } from '@/utils/typing'

import rms from '@/api/rms'
import { Parent, Zone, Region, TruncationRule } from '@/utils/domain'
import { identify, includes } from '@/utils/helpers'

const module: Module<ZoneState, RootState> = {
  namespaced: true,

  state: {
    available: {},
    current: null,
    _loading: false,
  },

  actions: {
    select: async ({ commit, state }, selected: Zone[]): Promise<void> => {
      for (const zone of Object.values(state.available)) {
        const toggled = includes(selected, zone)
        commit('SELECTED', { zone, toggled })
      }
    },
    current: async ({ commit, dispatch, state }, { id }): Promise<void> => {
      await dispatch('gaussianRandomFields/crossSections/fetch', { zone: id }, { root: true })
      commit('CURRENT', { id })
      await dispatch('truncationRules/preset/fetch', undefined, { root: true })

      const zone = state.available[`${id}`]
      await dispatch('parameters/grid/thickness', zone.name, { root: true })
      await dispatch('parameters/grid/simBox/thickness', zone.name, { root: true })
    },
    fetch: async ({ commit, dispatch, rootGetters }): Promise<void> => {
      commit('LOADING', true)
      try {
        await dispatch('populate', { zones: await rms.zones(rootGetters.gridModel) })
      } finally {
        commit('LOADING', false)
      }
    },
    populate: async ({ commit }, { zones }: { zones: (ZoneConfiguration)[]}): Promise<Zone[]> => {
      zones.forEach((zone): void => {
        if ('regions' in zone && Array.isArray(zone.regions)) {
          zone.regions = zone.regions.map((region): Region => new Region(region))
        }
      })
      const instances = zones.map((zone): Zone => new Zone(zone))
      instances.forEach((zone): void => {
        if (zone.regions) {
          zone.regions.forEach((region): void => {
            // @ts-ignore
            region.zone = zone
          })
        }
      })
      commit('AVAILABLE', identify(instances))
      return instances
    },
    conformity: async ({ commit }, { zone, value }): Promise<void> => {
      commit('CONFORMITY', { zone, value })
    },
  },

  mutations: {
    AVAILABLE: (state, zones): void => {
      Vue.set(state, 'available', zones)
    },
    SELECTED: (state, { zone, toggled }): void => {
      Vue.set(state.available[`${zone.id}`], 'selected', toggled)
    },
    CURRENT: (state, { id }): void => {
      Vue.set(state, 'current', id)
    },
    LOADING: (state, toggle): void => {
      Vue.set(state, '_loading', toggle)
    },
    CONFORMITY: (state, { zone, value }) => {
      Vue.set(state.available[`${zone.id}`], 'conformity', value)
    },
  },

  getters: {
    selected (state): ID[] {
      return Object.keys(state.available).filter((id): boolean => !!state.available[`${id}`].selected)
    },
    isFmuUpdatable: (state, getters, rootState): (zone: Zone) => boolean => (zone: Zone): boolean => {
      const belongsToZone = (item: Dependent): boolean => item.parent.zone === getId(zone) /* Ignore regions */

      const truncationRules = Object.values(rootState.truncationRules.available)
        .filter(rule => belongsToZone(rule))
      return truncationRules
        .some((rule: TruncationRule): boolean => rule.isFmuUpdatable)
    },
    byCode: (state): (zoneNumber: number, regionNumber: Optional<number>) => Parent => (zoneNumber: number, regionNumber: Optional<number> = null): Parent => {
      const zone = Object.values(state.available).find((zone): boolean => zone.code === zoneNumber)
      if (!zone) throw new APSError(`There are not Zones with code ${zoneNumber}`)
      let region = null
      if (regionNumber && regionNumber !== 0) {
        region = zone.regions.find((region): boolean => region.code === regionNumber)
        if (!region) throw new APSError(`The Zone with code ${zoneNumber}, does not have a region with code ${regionNumber}`)
      }
      return {
        zone,
        region,
      }
    }
  },
}

export default module
