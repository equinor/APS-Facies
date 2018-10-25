import { promiseSimpleCommit } from '@/store/utils'
import { Region } from '@/store/utils/domain'
import { makeData, selectItems, isEmpty } from '@/utils'
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
    select: ({ commit, dispatch, state }, items) => {
      const regions = selectItems({ state, items, _class: Region })
      dispatch('zones/update', { regions }, { root: true })
      return Promise.resolve(Object.keys(regions))
    },
    current: ({ commit }, { id }) => {
      return promiseSimpleCommit(commit, 'CURRENT', { id })
    },
    fetch: ({ dispatch, commit, rootState, rootGetters, state }, zoneId) => {
      if (state.use) {
        if (isEmpty(zoneId)) {
          const promises = Object.keys(rootState.zones.available)
            .map(id => {
              const zone = rootState.zones.available[`${id}`]
              return new Promise((resolve, reject) => {
                rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter)
                  .then(regions => {
                    resolve(dispatch('zones/update', { zoneId: id, regions: makeData(regions, Region) }, { root: true }))
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
      return dispatch('fetch', null)
    },
  },

  mutations: {
    AVAILABLE: (state, { regions }) => {
      state.available = regions
    },
    SELECTED: SELECTED_ITEMS,
    CURRENT: (state, { id }) => {
      state.current = id
    },
    USE: (state, value) => {
      state.use = value
    },
  },

  getters: {},
}
