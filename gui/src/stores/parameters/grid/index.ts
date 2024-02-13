import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { useGridModelStore } from '@/stores/grid-models'
import { useFmuMaxDepthStore } from '@/stores/fmu/maxDepth'
import { useParameterGridSimulationBoxStore } from './simulation-box'
import type { Coordinate3D } from '@/utils/domain/bases/interfaces'

export const useParameterGridStore = defineStore('parameter-grid', () => {
  const _waiting = ref(false)
  const azimuth = computed<number | null>(() => {
    const parameterStore = useParameterGridSimulationBoxStore()
    return parameterStore.azimuth
  })

  function $reset() {
    _waiting.value = false
    useParameterGridSimulationBoxStore()
      .$reset() // this resets simulation-boxes in turn
  }

  const waiting = computed(() => _waiting.value)

  const size = computed<Coordinate3D>(() => {
    const gridModelStore = useGridModelStore()
    const gridModel = gridModelStore.current
    if (!gridModel) return {
      x: null,
      y: null,
      z: null,
    }

    return gridModel.dimension
  })


  async function fetch(rough: boolean = false) {
    const gridModelStore = useGridModelStore()
    _waiting.value = true
    const simBoxStore = useParameterGridSimulationBoxStore()
    simBoxStore.rough = rough
    const gridModel = gridModelStore.current
    if (gridModel) {
      const fmuMaxDepthStore = useFmuMaxDepthStore()
      await fmuMaxDepthStore.fetch()
    }

    _waiting.value = false
  }

  const refresh = fetch

  return {
    azimuth,
    size,
    waiting,
    fetch,
    refresh,
    $reset,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterGridStore, import.meta.hot),
  )
}
