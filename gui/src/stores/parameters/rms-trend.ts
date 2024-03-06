import { acceptHMRUpdate, defineStore } from 'pinia'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import { APSError } from '@/utils/domain/errors'
import type { Ref } from 'vue'
import { ref } from 'vue'

export const useParameterRmsTrendStore = defineStore(
  'parameters-rms-trend',
  () => {
    const available = ref([]) as Ref<string[]>

    async function refresh() {
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      if (!gridModel) {
        throw new APSError("Can't refresh cubes without grid model.")
      }
      available.value = await rms.trendParameters(gridModel.name)
    }
    const fetch = refresh // alias

    function $reset() {
      available.value = []
    }

    return { available, fetch, refresh, $reset }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterRmsTrendStore, import.meta.hot),
  )
}
