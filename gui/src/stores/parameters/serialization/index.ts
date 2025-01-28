import type { DebugLevel } from '@/stores/parameters/debug-level'
import { useParameterDebugLevelStore } from '@/stores/parameters/debug-level'
import type { ParameterNameStoreSerialization } from '@/stores/parameters/names/serialization'
import { useParameterNameStoreSerialization } from '@/stores/parameters/names/serialization'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { useParametersToleranceOfProbabilityNormalisationStore } from '@/stores/parameters/tolerance'
import type {
  AvailableOptionSerialization,
  SelectableOptionSerialization,
  SelectableSerialization,
} from './helpers'
import { serializeOptionStore } from './helpers'
import { useParameterProbabilityCubeStore } from '@/stores/parameters/probability-cube'
import { useParameterRealizationStore } from '@/stores/parameters/realization'
import { useParameterRegionStore } from '@/stores/parameters/region'
import { useParameterRmsTrendStore } from '@/stores/parameters/rms-trend'
import {
  type TrendMap,
  useParameterRmsTrendMapZoneStore,
} from '@/stores/parameters/rms-trend-map-zones'
import {
  type TransformType,
  useParameterTransformTypeStore,
} from '@/stores/parameters/transform-type'
import { useParameterZoneStore } from '@/stores/parameters/zone'
import type { SimulationBoxesStoreSerialization } from '@/stores/parameters/grid/simulation-boxes'
import { useSimulationBoxesStoreSerialization } from '@/stores/parameters/grid/simulation-boxes'
import type { ProbabilityCube } from '@/utils/domain/facies/local'

export type ParameterStoreSerialization = {
  blockedWell: SelectableOptionSerialization
  blockedWellLog: SelectableOptionSerialization
  maxAllowedFractionOfValuesOutsideTolerance: SelectableSerialization<
    number,
    false
  >
  debugLevel: SelectableSerialization<DebugLevel, false>
  names: ParameterNameStoreSerialization
  probabilityCube: AvailableOptionSerialization<ProbabilityCube>
  realization: SelectableOptionSerialization
  region: SelectableOptionSerialization
  rmsTrend: AvailableOptionSerialization<string>
  rmsTrendMapZones: AvailableOptionSerialization<TrendMap>
  toleranceOfProbabilityNormalisation: SelectableSerialization<number, false>
  transformType: SelectableSerialization<TransformType, false>
  zone: SelectableSerialization
  grid: {
    simulationBox: SimulationBoxesStoreSerialization
  }
}

export function useParameterStoreSerialization(): ParameterStoreSerialization {
  return {
    blockedWell: serializeOptionStore(useParameterBlockedWellStore()),
    blockedWellLog: serializeOptionStore(useParameterBlockedWellLogStore()),
    maxAllowedFractionOfValuesOutsideTolerance: {
      selected:
        useParametersToleranceOfProbabilityNormalisationStore().tolerance,
    },
    debugLevel: { selected: useParameterDebugLevelStore().level },
    names: useParameterNameStoreSerialization(),
    probabilityCube: {
      available: useParameterProbabilityCubeStore().available,
    },
    realization: serializeOptionStore(useParameterRealizationStore()),
    region: serializeOptionStore(useParameterRegionStore()),
    rmsTrend: { available: useParameterRmsTrendStore().available },
    rmsTrendMapZones: {
      available: useParameterRmsTrendMapZoneStore().available,
    },
    toleranceOfProbabilityNormalisation: {
      selected:
        useParametersToleranceOfProbabilityNormalisationStore().tolerance,
    },
    transformType: { selected: useParameterTransformTypeStore().level },
    zone: { selected: useParameterZoneStore().selected },
    grid: {
      simulationBox: useSimulationBoxesStoreSerialization(),
    },
  }
}
