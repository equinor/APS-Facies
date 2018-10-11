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
          Object.keys(rootState.zones.available)
            .forEach(id => {
              const zone = rootState.zones.available[`${id}`]
              return rms.regions(rootGetters.gridModel, zone.name, rootGetters.regionParameter)
                .then(regions => {
                  dispatch('zones/update', { zoneId: id, regions: makeData(regions, Region) }, { root: true })
                })
            })
          zoneId = rootState.zones.current
        }
        return Promise.resolve(
          zoneId
            ? rootState.zones.available[`${zoneId}`].regions
            : []
        )
      }
    },
    use: ({ commit, state, rootGetters }, { use }) => {
      commit('USE', use)
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
