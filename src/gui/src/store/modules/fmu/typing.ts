import { OptionState } from '@/store/modules/options/typing'
import { Optional } from '@/utils/typing'

export interface FmuLayersState {
  value: Optional<number>
}

export interface SimulationGridModelsState {
  current: Optional<string>
}

export interface FmuState {
  maxDepth: FmuLayersState
  runFmuWorkflows: OptionState<boolean>
  create: OptionState<boolean>
  simulationGrid: SimulationGridModelsState
}
