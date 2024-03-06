import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import rms from '@/api/rms'

function defineToleranceStore(name: string) {
  return defineStore(`parameters-tolerance-${name}`, () => {
    const tolerance = ref<number>(0)
    function setTolerance(value: number) {
      tolerance.value = value
    }

    async function fetch() {
      const response = await rms.constants(name, 'tolerance')
      tolerance.value = response.tolerance
    }

    function $reset() {
      tolerance.value = 0
    }

    return { tolerance, setTolerance, fetch, $reset }
  })
}

export const useParametersMaxFractionOfValuesOutsideToleranceStore =
  defineToleranceStore('max_allowed_fraction_of_values_outside_tolerance')
export const useParametersToleranceOfProbabilityNormalisationStore =
  defineToleranceStore('max_allowed_deviation_before_error')

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(
      useParametersMaxFractionOfValuesOutsideToleranceStore,
      import.meta.hot,
    ),
  )
  import.meta.hot.accept(
    acceptHMRUpdate(
      useParametersToleranceOfProbabilityNormalisationStore,
      import.meta.hot,
    ),
  )
}
