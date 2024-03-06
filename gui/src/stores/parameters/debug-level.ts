import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'
import { displayWarning } from '@/utils/helpers/storeInteraction'

export type DebugLevel = 0 | 1 | 2 | 3 | 4

export function isDebugLevel(value: number): value is DebugLevel {
  return 0 <= value && value <= 4
}

export const useParameterDebugLevelStore = defineStore(
  'parameters-debug-level',
  () => {
    const selected = ref<DebugLevel>(1)

    function select(level: DebugLevel) {
      if (isDebugLevel(level)) {
        selected.value = level
      } else {
        // In relly old jobs, debug level may be undefined
        // also; trust, but verify
        displayWarning(`Tried to set debug level to an illegal value (${level}); must be between 0 and 4`)
      }
    }

    function $reset() {
      selected.value = 1
    }

    return {
        level: selected, // For reasons unknown, pinia exposes `level`, even though `selected` is exported 🤷
        select,
        $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterDebugLevelStore, import.meta.hot),
  )
}
