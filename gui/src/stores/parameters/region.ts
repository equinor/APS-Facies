import { acceptHMRUpdate, defineStore } from 'pinia'
import { useSelectableChoice } from './utils/selectable-choice'
import { useRegionStore } from '@/stores/regions'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import { APSError } from '@/utils/domain/errors'
import { useFaciesGlobalStore } from '@/stores/facies/global'
import { ref } from 'vue'

export const useParameterRegionStore = defineStore('parameter-region', () => {
  const { available, selected, $reset } = useSelectableChoice<string>()
  const loading = ref(false)

  async function select(regionParameter: string | null) {
    if (regionParameter !== null && !available.value.includes(regionParameter)) {
      throw new Error(
        `Selected regionParam ( ${regionParameter} ) ` +
          'is not present in the current project\n\n' +
          'Tip: RegionParamName in the APS model ' +
          `file must be one of { ${available.value.join()} }`,
      )
    }

    selected.value = regionParameter

    await useRegionStore()
      .setUse(!!regionParameter)

    await useFaciesGlobalStore()
      .refresh()
  }

  async function refresh() {
    loading.value = true
    const gridModelStore = useGridModelStore()
    const { current: gridModel} = gridModelStore
    if (!gridModel) {
      loading.value = false
      throw new APSError(
        "Can't refresh region parameter store without a selected grid model.",
      )
    }
    try {
      available.value = await rms.regionParameters(gridModel.name)
    } finally {
      loading.value = false
    }
  }

  async function fetch() {
    selected.value = null
    await refresh()
  }

  return { available, selected, select, refresh, fetch, $reset, loading }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterRegionStore, import.meta.hot),
  )
}
