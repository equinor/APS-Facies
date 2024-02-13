import { acceptHMRUpdate, defineStore } from 'pinia'
import { ref } from 'vue'

export type TransformType = 0 | 1

export function isTransformType(value: number): value is TransformType {
  return value === 0 || value === 1
}

export const useParameterTransformTypeStore = defineStore(
  'parameters-transform-type',
  () => {
    const level = ref<TransformType>(1)

    function select(value: TransformType) {
      if (value < 0 || value > 1) {
        throw Error(
          `The transform type MUST be between 0, and 1. (was ${value})`,
        )
      }
      level.value = value
    }

    function $reset() {
      level.value = 1
    }

    return { level, select, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterTransformTypeStore, import.meta.hot),
  )
}
