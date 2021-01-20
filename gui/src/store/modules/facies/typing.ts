import { ItemsState } from '@/utils/domain/bases/baseItem'
import { Identified } from '@/utils/domain/bases/interfaces'
import GlobalFacies from '@/utils/domain/facies/global'
import FaciesGroup from '@/utils/domain/facies/group'
import Facies from '@/utils/domain/facies/local'
import { Optional } from '@/utils/typing'

export interface GlobalFaciesState {
  available: Identified<GlobalFacies>
  current: Optional<GlobalFacies>

  _loading: boolean
  _inRms: GlobalFacies[]
}

export type FaciesGroupState = ItemsState<FaciesGroup>

export interface FaciesState extends ItemsState<Facies> {
  constantProbability: Identified<number>
  // TODO: These are modules, and should be removed, when the discovery issue with Vuex, and TypeScript
  //       has been resolved
  global: GlobalFaciesState
  groups: FaciesGroupState
}
