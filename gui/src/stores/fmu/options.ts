import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  DEFAULT_RUN_FMU_MODE,
  DEFAULT_RUN_ONLY_FMU_UPDATE,
  DEFAULT_CREATE_FMU_GRID,
  DEFAULT_FIELD_FORMAT,
  DEFAULT_EXTRAPOLATION_METHOD,
  DEFAULT_USE_RESIDUAL_FIELDS,
  DEFAULT_USE_NON_STANDARD_FMU_DIRS,
  DEFAULT_EXPORT_ERTBOX_GRID,
  DEFAULT_FMU_SIMULATION_GRID_NAME,
} from '@/config'

export const FIELD_FORMATS = ['roff', 'grdecl'] as const
export type FieldFormats = (typeof FIELD_FORMATS)[number]

export const TREND_EXTRAPOLATION_METHODS = [
  'extend_layer_mean',
  'repeat_layer_mean',
  'mean',
  'zero',
]
export type TrendExtrapolationMethod =
  (typeof TREND_EXTRAPOLATION_METHODS)[number]

type FmuOptions = {
  simulationGrid: string
  customTrendExtrapolationMethod: TrendExtrapolationMethod
  fieldFileFormat: FieldFormats

  create: boolean
  exportErtBoxGrid: boolean
  onlyUpdateFromFmu: boolean
  onlyUpdateResidualFields: boolean
  runFmuWorkflows: boolean
  useNonStandardFmu: boolean
}

export type FmuOptionStorePopulationData = Partial<FmuOptions>

export function defaultFmuOptions(): FmuOptions {
  return {
    simulationGrid: DEFAULT_FMU_SIMULATION_GRID_NAME,
    customTrendExtrapolationMethod: DEFAULT_EXTRAPOLATION_METHOD,
    fieldFileFormat: DEFAULT_FIELD_FORMAT,

    create: DEFAULT_CREATE_FMU_GRID,
    exportErtBoxGrid: DEFAULT_EXPORT_ERTBOX_GRID,
    onlyUpdateFromFmu: DEFAULT_RUN_ONLY_FMU_UPDATE,
    onlyUpdateResidualFields: DEFAULT_USE_RESIDUAL_FIELDS,
    runFmuWorkflows: DEFAULT_RUN_FMU_MODE,
    useNonStandardFmu: DEFAULT_USE_NON_STANDARD_FMU_DIRS,
  }
}

export const useFmuOptionStore = defineStore('fmu-options', () => {
  const options = ref<FmuOptions>(defaultFmuOptions())

  const fmuUpdatable = computed(
    () => options.value.runFmuWorkflows || options.value.onlyUpdateFromFmu,
  )

  const fmuMode = computed(
    () => options.value.runFmuWorkflows && !options.value.onlyUpdateFromFmu,
  )

  function populate(initial: Partial<FmuOptions>) {
    options.value = {
      ...options.value,
      ...initial,
    }
  }

  function $reset() {
    options.value = defaultFmuOptions()
  }

  return {
    options,
    fmuUpdatable,
    fmuMode,
    populate,
    $reset,
  }
})

export type FmuOptionsSerialization = FmuOptions

export function useFmuOptionsSerialization(): FmuOptionsSerialization {
  const { options } = useFmuOptionStore()

  // Same order as in the vuex exported store
  return {
    runFmuWorkflows: options.runFmuWorkflows,
    onlyUpdateFromFmu: options.onlyUpdateFromFmu,
    create: options.create,
    fieldFileFormat: options.fieldFileFormat,
    customTrendExtrapolationMethod: options.customTrendExtrapolationMethod,
    simulationGrid: options.simulationGrid,
    onlyUpdateResidualFields: options.onlyUpdateResidualFields,
    useNonStandardFmu: options.useNonStandardFmu,
    exportErtBoxGrid: options.exportErtBoxGrid,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useFmuOptionStore, import.meta.hot))
}
