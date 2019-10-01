import ProjectPathState from '@/store/modules/parameters/path/project/typing'
import { Selectable } from '@/store/modules/parameters/typing/helpers'

export default interface PathState {
  project: ProjectPathState
  fmuParameterListLocation: Selectable
}
