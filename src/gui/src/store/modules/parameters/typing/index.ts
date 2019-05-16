import NamesState from '@/store/modules/parameters/names/typing'
import PathState from '@/store/modules/parameters/path/typing'
import { Selectable } from '@/store/modules/parameters/typing/helpers'

export default interface ParametersState {
  path: PathState
  names: NamesState
  blockedWell: Selectable
  blockedWellLog: Selectable
  zone: Selectable
  region: Selectable
  realization: Selectable
  probabilityCube: {
    available: string[]
  }
}
