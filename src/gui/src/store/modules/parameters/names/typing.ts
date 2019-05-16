import ProjectNameState from '@/store/modules/parameters/names/project/typing'
import { Selectable } from '@/store/modules/parameters/typing/helpers'

export default interface NamesState {
  project: ProjectNameState
  workflow: Selectable
}
