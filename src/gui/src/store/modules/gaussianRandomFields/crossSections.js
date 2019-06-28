import Vue from 'vue'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import { DEFAULT_CROSS_SECTION } from '@/config'
import { getId } from '@/utils'
import { APSError } from '@/utils/domain/errors'

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
    async fetch ({ state, dispatch, rootGetters }, { zone = null, region = null } = {}) {
      const parent = {
        zone: zone || rootGetters.zone,
        region: region || rootGetters.region,
      }
      await dispatch('add', {
        type: DEFAULT_CROSS_SECTION.type,
        relativePosition: DEFAULT_CROSS_SECTION.position,
        parent,
      })
      return Object.values(state.available)
        .find(setting => setting.isChildOf({ zone, region }))
    },
    async populate ({ commit, dispatch, getters, rootState }, crossSections) {
      for (const crossSection of Object.values(crossSections)) {
        const existing = getters['byParent'](crossSection)
        if (existing && existing.id !== crossSection.id) {
          if (Object.values(rootState.gaussianRandomFields.fields).some(field => field.settings.crossSection.id === existing.id)) {
            throw new APSError('There is a conflict with the cross sections')
          }
          commit('DELETE', existing)
        }
        await dispatch('add', crossSection)
      }
    },
    add ({ commit, getters }, crossSection) {
      const existing = getters['byParent'](crossSection)
      if (!existing) {
        commit('ADD', new CrossSection({ ...crossSection }))
      }
    },
    async remove ({ commit, dispatch, rootState }, crossSection) {
      await Promise.all(Object.values(rootState.gaussianRandomFields.fields)
        .filter(field => getId(field.settings.crossSection) === getId(crossSection))
        .map(field => dispatch('gaussianRandomFields/remove', field, { root: true })))
      commit('DELETE', crossSection)
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
    DELETE (state, crossSection) {
      Vue.delete(state.available, crossSection.id)
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
      || null
    },
    byParent: (state) => ({ parent }) => {
      return Object.values(state.available)
        .find(item => item.isChildOf(parent)) || null
    },
    byId: (state) => (id) => {
      return state.available[`${getId(id)}`]
    }
  },
}
