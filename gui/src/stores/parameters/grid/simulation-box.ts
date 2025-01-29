import { acceptHMRUpdate, defineStore, storeToRefs } from 'pinia'
import { computed } from 'vue'
import { useGridModelStore } from '@/stores/grid-models'
import type { Coordinate2D } from '@/utils/domain/bases/interfaces'
import type { CODE } from '@/utils/domain/types'
import { useParameterGridSimulationBoxesStore } from './simulation-boxes'
import type { SimulationBoxSize as RmsSimulationBoxSize } from '@/api/types'

type SimulationBoxSize = {
  x: number | null
  y: number | null
  z: number | Record<CODE, number> | null
}

export const useParameterGridSimulationBoxStore = defineStore(
  'parameter-grid-simulation-box',
  () => {
    const store = useParameterGridSimulationBoxesStore()
    const { simulationBoxes, rough, waiting } = storeToRefs(store)
    const gridModelStore = useGridModelStore()

    const _simulationBox = computed<RmsSimulationBoxSize | null>(() => {
      if (!gridModelStore.current) return null
      const relevantSimulationBoxes =
        simulationBoxes.value[gridModelStore.current.name]
      if (!relevantSimulationBoxes /* may be undefined */) return null
      return (
        simulationBoxes.value[gridModelStore.current.name][
          rough.value ? 'true' : 'false'
        ] ?? null
      )
    })

    const size = computed<SimulationBoxSize>(() => {
      return (
        _simulationBox.value?.size ?? {
          x: null,
          y: null,
          z: null,
        }
      )
    })
    const origin = computed<Coordinate2D>(() => {
      return (
        _simulationBox.value?.origin ?? {
          x: null,
          y: null,
        }
      )
    })

    const azimuth = computed<number | null>(() => {
      return _simulationBox.value?.rotation ?? null
    })

    function $reset() {
      store.$reset()
    }

    return {
      waiting,
      rough,
      size,
      origin,
      azimuth,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterGridSimulationBoxStore, import.meta.hot),
  )
}
