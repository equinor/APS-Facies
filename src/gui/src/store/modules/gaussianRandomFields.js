import Vue from 'vue'
import { isEmpty, newSeed, notEmpty } from '@/utils'
import { GaussianRandomField } from '@/store/utils/domain'
import { ADD_ITEM } from '@/store/mutations'
import { addItem } from '@/store/actions'

const inNames = (state, name) => {
  for (const grfId in state.fields) {
    if (state.fields[`${grfId}`].name === name) return true
  }
  return false
}

const newGaussianFieldName = state => {
  const name = num => `GRF${num}`
  let grfNumber = Object.keys(state.fields).length + 1
  while (inNames(state, name(grfNumber))) {
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
      const remaining = minGaussianFields - Object.values(state.fields)
        .filter(field => field.parent.zone === zoneId).length
      for (let i = 0; i < remaining; i++) {
        dispatch('addEmptyField', { zoneId, regionId })
      }
      if (notEmpty(regionId)) {
        const relevantFields = Object.keys(state.fields)
          .filter(fieldId => {
            const field = state.fields[`${fieldId}`]
            return field.parent.zone === zoneId && isEmpty(field.parent.region)
          })
        relevantFields.forEach(fieldId => {
          const field = JSON.parse(JSON.stringify(state.fields[`${fieldId}`]))
          field.name = newGaussianFieldName(state)
          field.parent.region = regionId
          dispatch('addField', { field })
        })
      }
    },
    addEmptyField ({ dispatch, state, rootGetters }, { zoneId, regionId }) {
      dispatch('addField', {
        field: new GaussianRandomField({
          name: newGaussianFieldName(state),
          zone: zoneId || rootGetters.zone,
          region: regionId || rootGetters.region,
        })
      })
    },
    addField ({ commit, state }, { field }) {
      addItem({ commit }, { item: field })
    },
    deleteField ({ state, commit }, { grfId }) {
      if (state.fields.hasOwnProperty(grfId)) {
        commit('DELETE', { grfId })
      }
    },
    changeName ({ state, commit }, { grfId, name }) {
      setValue({ state, commit }, { grfId, value: name, commitName: 'CHANGE_NAME' })
    },
    changeSettings ({ state, commit }, { grfId, settings }) {
      setValue({ state, commit }, { grfId, value: settings, commitName: 'CHANGE_SETTINGS' })
    },
    newSeed ({ state, commit }, { grfId }) {
      const seed = {
        value: newSeed(),
        autoRenew: state.fields[`${grfId}`].settings.seed.autoRenew,
      }
      setValue({ state, commit }, { grfId, value: seed, commitName: 'CHANGE_SEED' })
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
    trendType ({ commit, state, rootState }, { grfId, value }) {
      setValue({ state, commit }, { grfId, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.trends.available, commitName: 'CHANGE_TREND_TYPE' })
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
      state.fields[`${grfId}`].name = value
    },
    CHANGE_SETTINGS (state, { grfId, value }) {
      state.fields[`${grfId}`].settings = value
    },
    CHANGE_SEED (state, { grfId, value }) {
      state.fields[`${grfId}`].settings.seed = value
    },
    // Variogram
    CHANGE_RANGE (state, { grfId, type, value }) {
      state.fields[`${grfId}`].variogram.range[`${type}`] = value
    },
    CHANGE_ANGLE (state, { grfId, variogramOrTrend, type, value }) {
      state.fields[`${grfId}`][`${variogramOrTrend}`].angle[`${type}`] = value
    },
    CHANGE_VARIOGRAM_TYPE (state, { grfId, value }) {
      state.fields[`${grfId}`].variogram.type = value
    },
    CHANGE_POWER (state, { grfId, value }) {
      state.fields[`${grfId}`].variogram.power = value
    },
    // Trend
    USE_TREND (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.use = value
    },
    CHANGE_TREND_TYPE (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.type = value
    },
    CHANGE_RELATIVE_STANDARD_DEVIATION (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.relativeStdDev = value
    },
    CHANGE_RELATIVE_SIZE_OF_ELLIPSE (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.relativeSize = value
    },
    CHANGE_STACKING_DIRECTION (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.stackingDirection = value
    },
    CHANGE_CURVATURE (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.curvature = value
    },
    CHANGE_ORIGIN_COORDINATE (state, { grfId, type, value }) {
      state.fields[`${grfId}`].trend.origin[`${type}`] = value
    },
    CHANGE_ORIGIN_TYPE (state, { grfId, value }) {
      state.fields[`${grfId}`].trend.origin.type = value
    },
  },

  getters: {
  },
}
