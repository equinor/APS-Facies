import { acceptHMRUpdate, defineStore } from 'pinia'
import { useParameterNameProjectStore } from './names/project'
import { useParameterNameWorkflowStore } from './names/workflow'
import {
    useParametersMaxFractionOfValuesOutsideToleranceStore,
    useParametersToleranceOfProbabilityNormalisationStore,
} from './tolerance'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { useParameterDebugLevelStore } from '@/stores/parameters/debug-level'
import { useParameterNameModelStore } from '@/stores/parameters/names/model'
import type { ParameterStoreSerialization } from '@/stores/parameters/serialization'
import { useParameterRealizationStore } from '@/stores/parameters/realization'
import { useParameterRegionStore } from '@/stores/parameters/region'
import { useParameterTransformTypeStore } from '@/stores/parameters/transform-type'
import { useParameterZoneStore } from '@/stores/parameters/zone'
import { useParameterGridSimulationBoxesStore } from '@/stores/parameters/grid/simulation-boxes'
import { useParameterGridStore } from '@/stores/parameters/grid'
import { useParameterProbabilityCubeStore } from '@/stores/parameters/probability-cube'
import { useParameterRmsTrendStore } from '@/stores/parameters/rms-trend'
import { useParameterRmsTrendMapZoneStore } from '@/stores/parameters/rms-trend-map-zones'

export const useParameterStore = defineStore('parameters', () => {
  const stores = [
      useParameterNameWorkflowStore(),
      useParameterNameProjectStore(),
      useParametersMaxFractionOfValuesOutsideToleranceStore(),
      useParametersToleranceOfProbabilityNormalisationStore(),
  ]
  async function fetch() {
    await Promise.all(stores.map(store => store.fetch()))
  }

  async function populate(parameters: ParameterStoreSerialization) {
      const blockedWellStore = useParameterBlockedWellStore()
      const blockedWellLogStore = useParameterBlockedWellLogStore()
      await blockedWellStore.select(parameters.blockedWell.selected)
      await blockedWellLogStore.select(parameters.blockedWellLog.selected)

      useParameterDebugLevelStore()
          .select(parameters.debugLevel.selected)

      useParametersMaxFractionOfValuesOutsideToleranceStore()
          .setTolerance(parameters.maxAllowedFractionOfValuesOutsideTolerance.selected)

      if (parameters.names.model.selected) {
          useParameterNameModelStore()
              .select(parameters.names.model.selected)
      }
      if (parameters.names.project.selected) {
          useParameterNameProjectStore()
              .select(parameters.names.project.selected)
      }
      if (parameters.names.workflow.selected) {
          useParameterNameWorkflowStore()
              .select(parameters.names.workflow.selected)
      }

      useParameterRealizationStore()
          .select(parameters.realization.selected)

      if (parameters.region.selected)
      await useParameterRegionStore()
          .select(parameters.region.selected)

      useParametersToleranceOfProbabilityNormalisationStore()
          .setTolerance(parameters.toleranceOfProbabilityNormalisation.selected)
      useParameterTransformTypeStore()
          .select(parameters.transformType.selected)

      if (parameters.zone.selected)
      useParameterZoneStore()
        .select(parameters.zone.selected)

      if (parameters.grid.simulationBox) {
          useParameterGridSimulationBoxesStore()
              .populate(parameters.grid.simulationBox)
      }
  }

  function $reset() {
    [
      useParameterGridStore(),
      useParameterNameModelStore(),
      useParameterNameProjectStore(),
      useParameterNameWorkflowStore(),
      useParameterBlockedWellStore(),
      useParameterBlockedWellLogStore(),
      useParameterDebugLevelStore(),
      useParameterProbabilityCubeStore(),
      useParameterRealizationStore(),
      useParameterRegionStore(),
      useParameterRmsTrendStore(),
      useParameterRmsTrendMapZoneStore(),
      useParametersMaxFractionOfValuesOutsideToleranceStore(),
      useParametersToleranceOfProbabilityNormalisationStore(),
      useParameterTransformTypeStore(),
      useParameterZoneStore(),
    ].forEach(store => store.$reset())
  }

  return { fetch, populate, $reset }
})


if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useParameterStore, import.meta.hot))
}
