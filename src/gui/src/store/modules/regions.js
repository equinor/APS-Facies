import Vue from 'vue'
import { promiseSimpleCommit } from '@/store/utils'
import { Region } from '@/utils/domain'
import { makeData, selectItems, isEmpty, notEmpty } from '@/utils'
import rms from '@/api/rms'
import { SELECTED_ITEMS } from '@/store/mutations'

export default {
  namespaced: true,

  state: {
    available: {},
    current: null,
    use: false,
  },

  modules: {},

  actions: {
    select: async ({ dispatch, state }, items) => {
      const regions = selectItems({ state, items, _class: Region })
      await dispatch('zones/update', { regions }, { root: true })
      return Object.keys(regions)
    },
    current: async ({ commit, dispatch }, { id }) => {
      await dispatch('truncationRules/resetTemplate', { type: '', template: '' }, { root: true })
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    fetch: ({ dispatch, commit, rootState, rootGetters, state }, zoneId) => {
      if (state.use && notEmpty(rootGetters.regionParameter)) {
        if (isEmpty(zoneId)) {
          const promises = Object.keys(rootState.zones.available)
            .map(id => {
              const zone = rootState.zones.available[`${id}`]
              return new Promise((resolve, reject) => {
                rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter)
                  .then(regions => {
                    regions = regions.map(region => { return { ...region, selected: !!zone.selected } })
                    resolve(dispatch('zones/update', { zoneId: id, regions: makeData(regions, Region, zone.regions) }, { root: true }))
                  })
              })
            })
          return Promise.all(promises)
        }
      }
      return Promise.resolve(
        zoneId
          ? rootState.zones.available[`${zoneId}`].regions
          : []
      )
    },
    use: ({ commit, dispatch }, { use }) => {
      commit('USE', use)
      commit('CURRENT', { id: null })
      return dispatch('fetch', null)
    },
    populate: async ({ commit, dispatch }, regions) => {
      commit('AVAILABLE', { regions })
      await dispatch('select', Object.values(regions).filter(({ selected }) => !!selected))
    },
  },

  mutations: {
    AVAILABLE: (state, { regions }) => {
      Vue.set(state, 'available', regions)
    },
    SELECTED: SELECTED_ITEMS,
    CURRENT: (state, { id }) => {
      Vue.set(state, 'current', id)
    },
    USE: (state, value) => {
      Vue.set(state, 'use', value)
    },
  },

  getters: {},
}
