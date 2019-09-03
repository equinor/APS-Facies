import GridParameterState from '@/store/modules/parameters/grid/typing'
import NamesState from '@/store/modules/parameters/names/typing'
import PathState from '@/store/modules/parameters/path/typing'
import { Selectable, SelectableChoice } from '@/store/modules/parameters/typing/helpers'

export default interface ParametersState {
  path: PathState
  names: NamesState
  blockedWell: SelectableChoice
  blockedWellLog: SelectableChoice
  zone: Selectable
  region: Selectable
  realization: Selectable
  grid: GridParameterState
  probabilityCube: {
    available: string[]
  }
}
