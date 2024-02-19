import { acceptHMRUpdate, defineStore } from 'pinia'
import { useSelectableChoice } from './utils/selectable-choice'
import rms from '@/api/rms'
import { APSError } from '@/utils/domain/errors'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterBlockedWellLogStore } from './blocked-well-log'
import { ref } from 'vue'

export const useParameterBlockedWellStore = defineStore(
  'parameter-blocked-well',
  () => {
    const { available, selected, $reset } = useSelectableChoice<string>()
    const loading = ref(false)

    async function select(blockedWell: string | null = null) {
      selected.value = blockedWell

      const blockedWellLogStore = useParameterBlockedWellLogStore()
      await blockedWellLogStore.select(null)
      await blockedWellLogStore.fetch()
    }

    async function fetch() {
      selected.value = null
      await refresh()
      const selection = available.value.length === 1 ? available.value[0] : null
      await select(selection)
    }

    async function refresh() {
      loading.value = true
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      if (!gridModel) {
        loading.value = false
        throw new APSError(
          "Can't refresh blocked well store without a selected grid model.",
        )
      }
      try {
        available.value = await rms.blockedWellParameters(gridModel.name)
      } finally {
        loading.value = false
      }
    }

    return {
      available,
      selected,
      select,
      fetch,
      refresh,
      $reset,
      loading,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterBlockedWellStore, import.meta.hot),
  )
}
