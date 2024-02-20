import { acceptHMRUpdate, defineStore } from 'pinia'
import type {
  GridModelConfiguration,
  GridModelSerialization,
} from '@/utils/domain/gridModel'
import GridModel from '@/utils/domain/gridModel'
import rms from '@/api/rms'
import { computed } from 'vue'
import type { ID } from '@/utils/domain/types'
import { isUUID } from '@/utils/helpers'
import { APSTypeError } from '@/utils/domain/errors'
import { useZoneStore } from './zones'
import { useCopyPasteStore } from './copy-paste'
import type {
  CurrentIdentifiedStorePopulationData,
  CurrentIdentifiedStoreSerialization
} from './utils/identified-items'
import {
  useCurrentIdentifiedItems,
} from './utils/identified-items'
import { useParameterRegionStore } from './parameters/region'
import { useParameterBlockedWellStore } from './parameters/blocked-well'
import { useParameterRmsTrendStore } from './parameters/rms-trend'
import { useParameterRmsTrendMapZoneStore } from './parameters/rms-trend-map-zones'
import { useParameterProbabilityCubeStore } from './parameters/probability-cube'
import { useParameterGridStore } from './parameters/grid'
import { useParameterRealizationStore } from './parameters/realization'
import { usePanelStore } from './panels'
import { useParameterGridSimulationBoxesStore } from '@/stores/parameters/grid/simulation-boxes'

export type GridModelStorePopulationData =
  CurrentIdentifiedStorePopulationData<GridModel>

type ParameterStoreDependentOnGrid = {
  fetch: () => Promise<void>
  refresh: () => Promise<void>
}
function getParameterStoresDependentOnGrid(): ParameterStoreDependentOnGrid[] {
  return [
    useParameterRegionStore(),
    useParameterBlockedWellStore(),
    useParameterRmsTrendStore(),
    // useParameterRmsTrendMapNamesStore(), // doesn't exist, didn't contain anything.
    useParameterRmsTrendMapZoneStore(),
    useParameterProbabilityCubeStore(),
    useParameterGridStore(),
    useParameterRealizationStore(),
  ]
}

export const useGridModelStore = defineStore('grid-models', () => {
  const { available, identifiedAvailable, currentId, current, $reset } =
    useCurrentIdentifiedItems<GridModel>()

  const names = computed(() => available.value.map((model) => model.name))

  async function select(gridModel: GridModel | ID | string, fetchSimbox: boolean = true) {
    const _gridModel =
      gridModel instanceof GridModel
        ? gridModel
        : isUUID(gridModel)
        ? identifiedAvailable.value[gridModel]
        : available.value.find((model) => model.name === gridModel)
    console.log('grid model', _gridModel)

    if (!_gridModel)
      throw new APSTypeError(`The grid model, ${gridModel} does not exist`)

    if (names.value.includes(_gridModel.name)) {
      currentId.value = _gridModel.id

      const panelStore = usePanelStore()
      panelStore.open('selection')

      const zoneStore = useZoneStore()
      await zoneStore.fetch()

      const parameterStoresDependentOnGrid = getParameterStoresDependentOnGrid()
      await Promise.all(
          [
              fetchSimbox && useParameterGridSimulationBoxesStore().updateSimulationBox(_gridModel),
              ...parameterStoresDependentOnGrid.map((store) => store.fetch()),
              ]
      )

      const copyPasteStore = useCopyPasteStore()
      copyPasteStore.copy(null)
    } else {
      throw new Error(
        `Selected grid model ( ${_gridModel.name} ) ` +
          'is not present in the current project.\n\n' +
          'Tip: GridModelName in the APS model file must be one of ' +
          `{ ${names.value.join()} }`,
      )
    }
  }

  function populate(
    gridModelDescriptions: (GridModelSerialization | GridModelConfiguration)[],
  ) {
    available.value = gridModelDescriptions.map((conf) => new GridModel(conf))
  }

  async function fetchGridModels(): Promise<GridModelConfiguration[]> {
    const rmsGridModels = await rms.gridModels()
    const gridModelConfigurations = await Promise.all(
      rmsGridModels.map(async (conf, index) => {
        const [x, y, z] = await rms.gridSize(conf.name)
        return {
          ...conf,
          order: index,
          dimension: { x, y, z },
        }
      }),
    )
    return gridModelConfigurations
  }

  async function fetch() {
    const gridModels = await fetchGridModels()
    populate(gridModels)
  }

  async function refresh() {
    const gridModelsByName = available.value.reduce(
      (map, grid) => map.set(grid.name, grid),
      new Map() as Map<string, GridModel>,
    )

    const gridModelConfigurations = (await fetchGridModels()).map((grid) => ({
      ...grid,
      id: gridModelsByName.get(grid.name)?.id,
    }))
    populate(gridModelConfigurations)

    const parameterStoresDependentOnGrid = getParameterStoresDependentOnGrid()
    await Promise.all(
      parameterStoresDependentOnGrid.map((store) => store.refresh()),
    )
  }

  return {
    available,
    identifiedAvailable,
    currentId,
    current,
    names,
    fetchGridModels,
    select,
    populate,
    fetch,
    refresh,
    $reset,
  }
})

export type GridModelStoreSerialization = CurrentIdentifiedStoreSerialization<GridModelSerialization>
export function useGridModelStoreSerialization(): GridModelStoreSerialization {
  const gridModelStore = useGridModelStore()
  return {
    available: gridModelStore.available.map((grid) => grid.toJSON()),
    current: gridModelStore.currentId,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useGridModelStore, import.meta.hot))
}
