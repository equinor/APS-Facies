import { OptionState } from '@/store/modules/options/typing'
import { Optional } from '@/utils/typing'

export interface FmuLayersState {
  value: Optional<number>
  minimum: number
}

export interface SimulationGridModelsState {
  current: Optional<string>
}

export interface FmuState {
  maxDepth: FmuLayersState
  runFmuWorkflows: OptionState<boolean>
  onlyUpdateFromFmu: OptionState<boolean>
  create: OptionState<boolean>
  simulationGrid: SimulationGridModelsState
  fieldFileFormat: OptionState<string>
  customTrendExtrapolationMethod: OptionState<string>
  onlyUpdateResidualFields: OptionState<boolean>
}
