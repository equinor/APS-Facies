import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import type { AllowedColorScales } from '@/config'
import {
  DEFAULT_AUTOFILL_OBSERVED_FACIES,
  DEFAULT_COLOR_SCALE,
  DEFAULT_EXPORT_FMU_CONFIG_FILES,
  DEFAULT_FACIES_AUTOFILL,
  DEFAULT_IMPORT_FIELDS_IN_FMU,
} from '@/config'

export type NameOrNumber = 'name' | 'number'

export type Options = {
  showNameOrNumber: {
    zone: NameOrNumber
    region: NameOrNumber
  }
  automaticAlphaFieldSelection: boolean
  filterZeroProbability: boolean
  automaticFaciesFill: boolean
  automaticObservedFaciesSelection: boolean
  exportFmuConfigFiles: boolean
  importFields: boolean
  colorScale: AllowedColorScales
}

export type OptionStorePopulationData = Partial<Options>
export type OptionStoreSerialization = Options

function defaultOptions(): Options {
  return {
    showNameOrNumber: {
      zone: 'number',
      region: 'number',
    },
    automaticAlphaFieldSelection: true,
    filterZeroProbability: false,
    automaticFaciesFill: DEFAULT_FACIES_AUTOFILL,
    automaticObservedFaciesSelection: DEFAULT_AUTOFILL_OBSERVED_FACIES,
    exportFmuConfigFiles: DEFAULT_EXPORT_FMU_CONFIG_FILES,
    importFields: DEFAULT_IMPORT_FIELDS_IN_FMU,
    colorScale: DEFAULT_COLOR_SCALE,
  }
}

export const useOptionStore = defineStore('options', () => {
  const options = ref<Options>(defaultOptions())

  function populate(initial: OptionStorePopulationData) {
    options.value = {
      ...options.value,
      ...initial,
    }
  }

  function $reset() {
    options.value = defaultOptions()
  }

  return { options, populate, $reset }
})

export function useOptionStoreSerialization(): OptionStoreSerialization {
  const optionStore = useOptionStore()
  return {
    ...optionStore.options,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useOptionStore, import.meta.hot))
}
