import { acceptHMRUpdate, defineStore } from 'pinia'
import type { Ref } from 'vue'
import { ref } from 'vue'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import { APSError } from '@/utils/domain/errors'
import type { ProbabilityCube } from '@/utils/domain/facies/local'

export const useParameterProbabilityCubeStore = defineStore(
  'parameters-probability-cube',
  () => {
    const available = ref([]) as Ref<ProbabilityCube[]>

    async function refresh() {
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      if (!gridModel) {
        throw new APSError("Can't refresh cubes without grid model.")
      }
      available.value = await rms.probabilityCubeParameters(gridModel.name)
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
    acceptHMRUpdate(useParameterProbabilityCubeStore, import.meta.hot),
  )
}
