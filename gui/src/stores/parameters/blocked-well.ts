import { acceptHMRUpdate, defineStore } from 'pinia'
import { useSelectableChoice } from './utils/selectable-choice'
import rms from '@/api/rms'
import { APSError } from '@/utils/domain/errors'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterBlockedWellLogStore } from './blocked-well-log'

export const useParameterBlockedWellStore = defineStore(
  'parameter-blocked-well',
  () => {
    const { available, selected, $reset } = useSelectableChoice<string>()

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
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      if (!gridModel) {
        throw new APSError(
          "Can't refresh blocked well store without a selected grid model.",
        )
      }
      available.value = await rms.blockedWellParameters(gridModel.name)
    }

    return {
      available,
      selected,
      select,
      fetch,
      refresh,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterBlockedWellStore, import.meta.hot),
  )
}
