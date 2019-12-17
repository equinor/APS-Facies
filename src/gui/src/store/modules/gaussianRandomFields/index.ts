import { Context as RootContext, RootState } from '@/store/typing'
import { Region } from '@/utils/domain'
import { GaussianRandomFieldState } from '@/store/modules/gaussianRandomFields/typing'
import { ID } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'
import Vue from 'vue'

import { getId, hasParents, newSeed } from '@/utils'
import GaussianRandomField, {
  Trend,
  Variogram,
  GaussianRandomFieldSerialization
} from '@/utils/domain/gaussianRandomField'

import crossSections from '@/store/modules/gaussianRandomFields/crossSections'
import rms from '@/api/rms'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import { unpackVariogram } from '@/utils/domain/gaussianRandomField/variogram'
import { unpackTrend } from '@/utils/domain/gaussianRandomField/trend'
import { Module } from 'vuex'

type Context = RootContext<GaussianRandomFieldState, RootState>

function setValue (
  { state, commit }: Context,
  { commitName, field, type, legalTypes, variogramOrTrend, value }: { commitName: string, field: GaussianRandomField, type?: string, legalTypes?: string[], variogramOrTrend?: 'variogram' | 'trend', value: any }
): void {
  const checks: ([() => boolean, string])[] = [
    [
      (): boolean => state.available.hasOwnProperty(field.id),
      `The gaussian field (${field}) does not exists`
    ],
    [
      // @ts-ignore
      (): boolean => typeof type === 'undefined' || legalTypes.indexOf(type) !== -1,
      `The type '${type}' is not a legal value (${legalTypes})`
    ],
    [
      (): boolean => typeof variogramOrTrend === 'undefined' || ['variogram', 'trend'].indexOf(variogramOrTrend) >= 0,
      `When specifying 'variogramOrTrend', is MUST be either 'variogram', or 'trend'`
    ],
  ]
  checks.forEach(([check, errorMessage]): void => {
    if (!check()) throw new Error(errorMessage)
  })
  commit(commitName, { field, type, variogramOrTrend, value })
}

function getRelevantFields (state: GaussianRandomFieldState, zone: Zone, region: Region): GaussianRandomField[] {
  const zoneId = zone.id || zone
  const regionId = region ? (region.id || region) : null
  return Object.values(state.available)
    .filter((field): boolean => hasParents(field, zoneId, regionId))
}

function newGaussianFieldName (state: GaussianRandomFieldState, zone: Zone, region: Region): string {
  const name = (num: number): string => `GRF${num}`
  const relevant = (): GaussianRandomField[] => getRelevantFields(state, zone, region)

  let grfNumber = relevant().length + 1
  while (relevant().find((field): boolean => field.name === name(grfNumber))) {
    grfNumber += 1
  }
  return name(grfNumber)
}

interface Field {
  field: GaussianRandomField
}

const module: Module<GaussianRandomFieldState, RootState> = {
  namespaced: true,

  state: {
    available: {
    },
  },

  modules: {
    crossSections,
  },

  actions: {
    async populate ({ dispatch }, fields: (GaussianRandomField | GaussianRandomFieldSerialization)[]): Promise<void> {
      await Promise.all(fields.map((field): Promise<void> => {
        return dispatch('add', field)
      }))
    },
    async addEmptyField ({ dispatch, state, rootGetters }, { zone, region } = {}): Promise<GaussianRandomField> {
      zone = zone || rootGetters.zone
      region = region || rootGetters.region
      const field = new GaussianRandomField({
        name: newGaussianFieldName(state, zone, region),
        crossSection: await dispatch('crossSections/fetch', { zone, region }),
        zone,
        region,
      })
      await dispatch('add', field)
      return field
    },
    add ({ commit, getters }, field): void {
      if (!(field instanceof GaussianRandomField)) {
        field = new GaussianRandomField({
          ...field,
          variogram: new Variogram(unpackVariogram(field.variogram)),
          trend: new Trend(unpackTrend(field.trend)),
          crossSection: getters['crossSections/byId'](field.settings.crossSection),
        })
      }
      commit('ADD', field)
    },
    async remove ({ commit, dispatch }, field: GaussianRandomField): Promise<void> {
      await dispatch('truncationRules/deleteField', { field }, { root: true })
      commit('DELETE', { field })
    },
    async deleteField ({ state, commit, dispatch }, { field }: Field): Promise<void> {
      if (state.available.hasOwnProperty(field.id)) {
        await dispatch('truncationRules/deleteField', { field }, { root: true })
        commit('DELETE', { field })
      }
    },
    async updateSimulation ({ commit, dispatch, rootGetters }, { field }): Promise<void> {
      commit('CHANGE_WAITING', { field, value: true })
      try {
        await dispatch('updateSimulationData', {
          field,
          data: await rms.simulateGaussianField({
            name: field.name,
            variogram: field.variogram,
            trend: field.trend,
            settings: rootGetters['simulationSettings']({ field }),
          })
        })
      } finally {
        commit('CHANGE_WAITING', { field, value: false })
      }
    },
    async updateSimulations ({ dispatch, state }, { fields, all = false }: { fields: (GaussianRandomField | ID)[], all: boolean }): Promise<void> {
      const _fields: GaussianRandomField[] = fields
        .map((field): GaussianRandomField => !(field instanceof GaussianRandomField)
          ? state.available[`${field}`]
          : field
        )
      const notSimulated = all ? _fields : _fields.filter((field): boolean => !field.simulated)
      if (notSimulated.length > 0) {
        await Promise.all(notSimulated.map((field): Promise<void> => dispatch('updateSimulation', { field })))
      }
    },
    updateSimulationData (context, { field, data }): void {
      setValue(context, { field, value: data, commitName: 'CHANGE_SIMULATION' })
    },
    changeName (context, { field, name }): void {
      setValue(context, { field, value: name, commitName: 'CHANGE_NAME' })
    },
    changeSettings (context, { field, settings }): void {
      setValue(context, { field, value: settings, commitName: 'CHANGE_SETTINGS' })
    },
    changeValidity ({ commit }, { field, value }): void {
      commit('CHANGE_VALIDITY', { field, value })
    },
    newSeed (context, { field }): void {
      setValue(context, { field, value: newSeed(), commitName: 'CHANGE_SEED' })
    },
    seed (context, { field, value }): void {
      setValue(context, { field, value, commitName: 'CHANGE_SEED' })
    },
    overlay (context, { field, value }): void {
      setValue(context, { field, value, commitName: 'CHANGE_OVERLAY' })
    },
    // TODO: check values are appropriate
    // Variogram
    range (context, { field, type, value }): void {
      setValue(context, { field, type, value, legalTypes: ['main', 'perpendicular', 'vertical'], commitName: 'CHANGE_RANGE' })
    },
    angle (context, { field, variogramOrTrend, type, value }): void {
      const legalTypes = variogramOrTrend === 'variogram' ? ['azimuth', 'dip'] : ['azimuth', 'stacking', 'migration']
      setValue(context, { field, type, variogramOrTrend, value, legalTypes, commitName: 'CHANGE_ANGLE' })
    },
    variogramType (context, { field, value }): void {
      const { rootState } = context
      setValue(context, { field, value, type: value, legalTypes: rootState.constants.options.variograms.available, commitName: 'CHANGE_VARIOGRAM_TYPE' })
    },
    power (context, { field, value }): void {
      setValue(context, { field, value, commitName: 'CHANGE_POWER' })
    },
    // Trend
    useTrend (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'USE_TREND' })
    },
    relativeStdDev (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_STANDARD_DEVIATION' })
    },
    relativeSize (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RELATIVE_SIZE_OF_ELLIPSE' })
    },
    async trendType (context, { field, value }): Promise<void> {
      const { dispatch, rootState } = context
      setValue(context, { field, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.trends.available, commitName: 'CHANGE_TREND_TYPE' })
      if (field.trend.type === 'HYPERBOLIC') {
        const curvature = field.trend.curvature
        if (curvature.value <= 1) {
          await dispatch('curvature', { field, value: new FmuUpdatableValue(1.01, curvature.updatable) })
        }
      }
    },
    trendParameter (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'CHANGE_RMS_TREND_PARAM' })
    },
    stackingDirection (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'CHANGE_STACKING_DIRECTION' })
    },
    curvature (context, { field, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', value, commitName: 'CHANGE_CURVATURE' })
    },
    originType (context, { field, value }): void {
      const { rootState } = context
      setValue(context, { field, variogramOrTrend: 'trend', value, type: value, legalTypes: rootState.constants.options.origin.available, commitName: 'CHANGE_ORIGIN_TYPE' })
    },
    origin (context, { field, type, value }): void {
      setValue(context, { field, variogramOrTrend: 'trend', type, value, legalTypes: ['x', 'y', 'z'], commitName: 'CHANGE_ORIGIN_COORDINATE' })
    },
  },

  mutations: {
    // Gaussian Random Field
    ADD (state, field): void {
      Vue.set(state.available, field.id, field)
    },
    DELETE (state, { field }): void {
      Vue.delete(state.available, field.id)
    },
    CHANGE_NAME (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'name', value)
    },
    CHANGE_SETTINGS (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'settings', value)
    },
    CHANGE_SEED (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].settings, 'seed', value)
    },
    CHANGE_SIMULATION (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'simulation', value)
    },
    CHANGE_OVERLAY (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'overlay', value)
    },
    CHANGE_WAITING (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'waiting', value)
    },
    CHANGE_VALIDITY (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`], 'valid', value)
    },
    // Variogram
    CHANGE_RANGE (state, { field, type, value }): void {
      Vue.set(state.available[`${field.id}`].variogram.range, type, value)
    },
    CHANGE_ANGLE (state, { field, variogramOrTrend, type, value }): void {
      Vue.set(state.available[`${field.id}`][`${variogramOrTrend}`].angle, type, value)
    },
    CHANGE_VARIOGRAM_TYPE (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].variogram, 'type', value)
    },
    CHANGE_POWER (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].variogram, 'power', value)
    },
    // Trend
    USE_TREND (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'use', value)
    },
    CHANGE_TREND_TYPE (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'type', value)
    },
    CHANGE_RELATIVE_STANDARD_DEVIATION (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'relativeStdDev', value)
    },
    CHANGE_RELATIVE_SIZE_OF_ELLIPSE (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'relativeSize', value)
    },
    CHANGE_STACKING_DIRECTION (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'stackingDirection', value)
    },
    CHANGE_CURVATURE (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend, 'curvature', value)
    },
    CHANGE_ORIGIN_COORDINATE (state, { field, type, value }): void {
      Vue.set(state.available[`${field.id}`].trend.origin, type, value)
    },
    CHANGE_ORIGIN_TYPE (state, { field, value }): void {
      Vue.set(state.available[`${field.id}`].trend.origin, 'type', value)
    },
    CHANGE_RMS_TREND_PARAM (state, { field, value }): void {
      state.available[`${field.id}`].trend.parameter = value
    }
  },

  getters: {
    byId: (state): (id: ID) => GaussianRandomField | undefined => (id: ID): GaussianRandomField | undefined => {
      return state.available[`${getId(id)}`]
    },
  },
}

export default module
