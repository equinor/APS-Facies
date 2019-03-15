import Vue from 'vue'
import uuidv4 from 'uuid/v4'

import { hasParents, newSeed, notEmpty } from '@/utils'
import { GaussianRandomField } from '@/store/utils/domain'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'
import { cloneDeep } from 'lodash'
import { Trend, Variogram } from '@/store/utils/domain/gaussianRandomField'

const makeFieldData = (fields) => {
  return fields.reduce((data, field) => {
    const instance = new GaussianRandomField({
      variogram: new Variogram(field.variogram || {}),
      trend: new Trend(field.trend || {}),
      ...field,
    })
    data[instance.id] = instance
    return data
  }, {})
}

const newGaussianFieldName = (state, zone, region) => {
  const name = num => `GRF${num}`
  const relevant = () => getRelevantFields(state, zone, region)

  let grfNumber = relevant().length + 1
  while (relevant().find((field) => field.name === name(grfNumber))) {
    grfNumber += 1
  }
  return name(grfNumber)
}

const setValue = ({ state, commit }, { commitName, grfId, type, legalTypes, variogramOrTrend, value }) => {
  const checks = [
    [
      () => state.fields.hasOwnProperty(grfId),
      `The gaussian field (${grfId}) does not exists`
    ],
    [
      () => typeof type === 'undefined' || legalTypes.indexOf(type) !== -1,
      `The type '${type}' is not a legal value (${legalTypes})`
    ],
    [
      () => typeof variogramOrTrend === 'undefined' || ['variogram', 'trend'].indexOf(variogramOrTrend) >= 0,
      `When specifying 'variogramOrTrend', is MUST be either 'variogram', or 'trend'`
    ],
  ]
  checks.forEach(([check, errorMessage]) => {
    if (!check()) throw new Error(errorMessage)
  })
  commit(commitName, { grfId, type, variogramOrTrend, value })
}

const getRelevantFields = (state, zone, region) => {
  const zoneId = zone.id || zone
  const regionId = region ? (region.id || region) : undefined
  return Object.values(state.fields)
    .filter(field => hasParents(field, zoneId, regionId))
}

export default {
  namespaced: true,

  state: {
    fields: {
    }
  },

  modules: {
  },

  actions: {
    init ({ state, dispatch, rootState, rootGetters }, { zoneId, regionId }) {
      const minGaussianFields = rootGetters['constants/numberOf/gaussianRandomFields/minimum']
      const remaining = minGaussianFields - getRelevantFields(state, zoneId, regionId).length
      if (notEmpty(regionId) && remaining > 0) {
        getRelevantFields(state, zoneId)
          .forEach(field => {
            field = cloneDeep(field)
            field._id = uuidv4()
            field.name = newGaussianFieldName(state, zoneId, regionId)
            field.parent.region = regionId
            dispatch('addField', { field })
          })
      } else {
        for (let i = 0; i < remaining; i++) {
          dispatch('addEmptyField', { zone: zoneId, region: regionId })
        }
      }
    },
    populate ({ dispatch }, fields) {
      return Promise.all(Object.values(makeFieldData(fields)).map(field => dispatch('addField', { field })))
    },
    addEmptyField ({ dispatch, state, rootGetters }, { zone, region } = {}) {
      zone = zone || rootGetters.zone
      region = region || rootGetters.region
      return dispatch('addField', {
        field: new GaussianRandomField({
          name: newGaussianFieldName(state, zone, region),
          zone,
          region,
        })
      })
    },
    addField ({ commit, state }, { field }) {
      return addItem({ commit }, { item: field })
    },
    async deleteField ({ state, commit, dispatch, rootState }, { grfId }) {
      if (state.fields.hasOwnProperty(grfId)) {
        await dispatch('truncationRules/deleteField', { grfId }, { root: true })
        commit('DELETE', { grfId })
      }
    },
    updateSimulationData ({ commit, state }, { grfId, data }) {
      setValue({ state, commit }, { grfId, value: data, commitName: 'CHANGE_SIMULATION' })
    },
    changeName ({ state, commit }, { grfId, name }) {
      setValue({ state, commit }, { grfId, value: name, commitName: 'CHANGE_NAME' })
    },
    changeSettings ({ state, commit }, { grfId, settings }) {
      setValue({ state, commit }, { grfId, value: settings, commitName: 'CHANGE_SETTINGS' })
    },
    newSeed ({ state, commit }, { grfId }) {
      setValue({ state, commit }, { grfId, value: newSeed(), commitName: 'CHANGE_SEED' })
    },
    seed ({ state, commit }, { grfId, value }) {
      setValue({ state, commit }, { grfId, value, commitName: 'CHANGE_SEED' })
    },
    // TODO: check values are appropriate
    // Variogram
    range ({ state, commit }, { grfId, type, value }) {
      setValue({ state, commit }, { grfId, type, value, legalTypes: ['main', 'perpendicular', 'vertical'], commitName: 'CHANGE_RANGE' })
    },
    angle ({ commit, state }, { grfId, variogramOrTrend, type, value }) {
      const legalTypes = variogramOrTrend === 'variogram' ? ['azimuth', 'dip'] : ['azimuth', 'stacking', 'migration']
      setValue({ state, commit }, { grfId, type, variogramOrTrend, value, legalTypes, commitName: 'CHANGE_ANGLE' })
    },
    variogramType ({ commit, state, rootState }, { grfId, value }) {
      setValue({ state, commit }, { grfId, value, type: value, legalTypes: rootState.constants.options.variograms.available, commitName: 'CHANGE_VARIOGRAM_TYPE' })
    },
    power ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, value, commitName: 'CHANGE_POWER' })
    },
    // Trend
    useTrend ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'USE_TREND' })
    },
    relativeStdDev ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_STANDARD_DEVIATION' })
    },
    relativeSize ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_SIZE_OF_ELLIPSE' })
    },
    trendType ({ commit, dispatch, state, rootState }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.trends.available, commitName: 'CHANGE_TREND_TYPE' })
      const field = state.fields[`${grfId}`]
      if (field.trend.type === 'HYPERBOLIC' && field.trend.curvature.value <= 1) {
        dispatch('curvature', { grfId, value: 1.01 })
      }
    },
    trendParameter ({ commit, state, rootState }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RMS_TREND_PARAM' })
    },
    stackingDirection ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_STACKING_DIRECTION' })
    },
    curvature ({ commit, state }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, commitName: 'CHANGE_CURVATURE' })
    },
    originType ({ commit, state, rootState }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.origin.available, commitName: 'CHANGE_ORIGIN_TYPE' })
    },
    origin ({ commit, state }, { grfId, type, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', type, value, legalTypes: ['x', 'y', 'z'], commitName: 'CHANGE_ORIGIN_COORDINATE' })
    },
  },

  mutations: {
    ADD (state, { id, item }) {
      ADD_ITEM(state.fields, { id, item })
    },
    DELETE (state, { grfId }) {
      Vue.delete(state.fields, grfId)
    },
    CHANGE_NAME (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`], 'name', value)
    },
    CHANGE_SETTINGS (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`], '_settings', value)
    },
    CHANGE_SEED (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].settings, 'seed', value)
    },
    CHANGE_SIMULATION (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`], '_data', value)
    },
    // Variogram
    CHANGE_RANGE (state, { grfId, type, value }) {
      Vue.set(state.fields[`${grfId}`].variogram.range, type, value)
    },
    CHANGE_ANGLE (state, { grfId, variogramOrTrend, type, value }) {
      Vue.set(state.fields[`${grfId}`][`${variogramOrTrend}`].angle, type, value)
    },
    CHANGE_VARIOGRAM_TYPE (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].variogram, 'type', value)
    },
    CHANGE_POWER (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].variogram, 'power', value)
    },
    // Trend
    USE_TREND (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'use', value)
    },
    CHANGE_TREND_TYPE (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'type', value)
    },
    CHANGE_RELATIVE_STANDARD_DEVIATION (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'relativeStdDev', value)
    },
    CHANGE_RELATIVE_SIZE_OF_ELLIPSE (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'relativeSize', value)
    },
    CHANGE_STACKING_DIRECTION (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'stackingDirection', value)
    },
    CHANGE_CURVATURE (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend, 'curvature', value)
    },
    CHANGE_ORIGIN_COORDINATE (state, { grfId, type, value }) {
      Vue.set(state.fields[`${grfId}`].trend.origin, type, value)
    },
    CHANGE_ORIGIN_TYPE (state, { grfId, value }) {
      Vue.set(state.fields[`${grfId}`].trend.origin, 'type', value)
    },
    CHANGE_RMS_TREND_PARAM (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.rmsTrendParam = value
    }
  },

  getters: {
  },
}
