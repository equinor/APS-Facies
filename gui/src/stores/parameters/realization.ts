import { acceptHMRUpdate, defineStore } from 'pinia'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import { APSError } from '@/utils/domain/errors'
import { useSelectableChoice } from './utils/selectable-choice'
import { DEFAULT_FACIES_REALIZATION_PARAMETER_NAME } from '@/config'

export const useParameterRealizationStore = defineStore(
  'parameters-realization',
  () => {
    const { available, selected, $reset } = useSelectableChoice<string>()

    function select(value: string | null) {
      selected.value = value
    }

    async function fetch() {
      select(DEFAULT_FACIES_REALIZATION_PARAMETER_NAME)
      await refresh()
    }

    async function refresh() {
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      if (!gridModel) {
        throw new APSError("Can't refresh realizations without grid model.")
      }
      available.value = await rms.realizationParameters(gridModel.name)
    }

    return {
      available,
      selected,
      fetch,
      refresh,
      select,
      $reset,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterRealizationStore, import.meta.hot),
  )
}
