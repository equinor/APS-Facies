import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import rms from '@/api/rms'
import type { LengthUnit } from '@/api/types'
import { displayWarning } from '@/utils/helpers/storeInteraction'

export const useParameterLengthUnitStore = defineStore(
  'parameter-length-unit',
  () => {
    const selected = ref<LengthUnit>()

    async function fetch() {
      try {
        selected.value = await rms.lengthUnit()
      } catch (error) {
        selected.value = undefined
        displayWarning(
          `Could not determine the RMS project's length unit; length values will be shown without a unit.\n${error}`,
        )
      }
    }

    function $reset() {
      selected.value = undefined
    }

    return {
      selected,
      fetch,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterLengthUnitStore, import.meta.hot),
  )
}
