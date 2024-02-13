import { acceptHMRUpdate, defineStore } from 'pinia'
import { reactive } from 'vue'
import { useZoneStore } from '@/stores/zones'
import { useGridModelStore } from '@/stores/grid-models'

export interface FmuMaxDepth {
  value: number | null
  minimum: number
}

export const useFmuMaxDepthStore = defineStore('fmu-max-depth', () => {
  const maxDepth = reactive<FmuMaxDepth>({
    value: null,
    minimum: 0,
  })

  function set(value: number | null) {
    maxDepth.value = value
  }
  /** @deprecated */
  const populate = set // alias

  async function fetch(value: number | null = null) {
    if (value && value !== 0) {
      maxDepth.value = value
      return
    }

    const zoneStore = useZoneStore()
    const zones = zoneStore.available
    if (zones.length > 0) {
      const minimum = Math.max(...zones.map((zone) => zone.thickness))
      maxDepth.value = minimum
      maxDepth.minimum = minimum
    } else {
      const gridModelStore = useGridModelStore()
      const grid = gridModelStore.current
      if (grid) {
        maxDepth.value = grid.dimension.z
      }
    }
  }

  function $reset() {
    maxDepth.value = null
    maxDepth.minimum = 0
  }

  return {
    maxDepth,
    set,
    populate,
    fetch,
    $reset,
  }
})

export type FmuMaxDepthStoreSerialization = {
  value: number | null
  minimum: number
}

export function useFmuMaxDepthStoreSerialization (): FmuMaxDepthStoreSerialization {
  const { maxDepth } = useFmuMaxDepthStore()
  return {
    value: maxDepth.value,
    minimum: maxDepth.minimum,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useFmuMaxDepthStore, import.meta.hot))
}
