import Vue from 'vue'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import { DEFAULT_CROSS_SECTION } from '@/config'
import { getId } from '@/utils'

async function updateAffectedFields ({ state, rootGetters, dispatch }, id) {
  const crossSection = state.available[`${id}`]
  const relevantFields = Object.values(rootGetters.allFields.filter(field => field.isChildOf(crossSection.parent)))
  await Promise.all(relevantFields
    .map(field => dispatch('gaussianRandomFields/updateSimulation', { grfId: field.id }, { root: true }))
  )
}

export default {
  namespaced: true,

  state: {
    available: {},
  },

  actions: {
    fetch ({ state, commit, rootGetters }, { zone = null, region = null } = {}) {
      zone = zone || rootGetters.zone
      region = region || rootGetters.region
      let crossSection = Object.values(state.available)
        .find(setting => setting.isChildOf({ zone, region }))
      if (!crossSection) {
        crossSection = new CrossSection({
          type: DEFAULT_CROSS_SECTION.type,
          relativePosition: DEFAULT_CROSS_SECTION.position,
          parent: {
            zone: zone,
            region: region,
          }
        })
        commit('ADD', crossSection)
      }
      return crossSection
    },
    populate ({ commit }, crossSections) {
      Object.values(crossSections)
        .forEach(crossSection => {
          if (!(crossSection instanceof CrossSection)) {
            crossSection = new CrossSection({ ...crossSection })
          }
          commit('ADD', crossSection)
        })
    },
    async changeType ({ state, commit, dispatch, rootGetters }, { id, type }) {
      commit('CHANGE_TYPE', { id, type })
      await updateAffectedFields({ state, rootGetters, dispatch }, id)
    },
    async changeRelativePosition ({ commit, state, dispatch, rootGetters }, { id, relativePosition }) {
      commit('CHANGE_RELATIVE_POSITION', { id, relativePosition })
      await updateAffectedFields({ state, dispatch, rootGetters }, id)
    },
  },

  mutations: {
    ADD (state, crossSection) {
      Vue.set(state.available, crossSection.id, crossSection)
    },
    CHANGE_TYPE (state, { id, type }) {
      Vue.set(state.available[`${id}`], 'type', type)
    },
    CHANGE_RELATIVE_POSITION (state, { id, relativePosition }) {
      Vue.set(state.available[`${id}`], 'relativePosition', relativePosition)
    },

  },

  getters: {
    current (state, getters, rootState, rootGetters) {
      return Object.values(state.available)
        .find(crossSection => crossSection.isChildOf({ zone: rootGetters.zone, region: rootGetters.region }))
    },
    byId: (state) => (id) => {
      return state.available[`${getId(id)}`]
    }
  },
}
