import { ItemsState } from '@/utils/domain/bases/baseItem'
import Zone, { Region } from '@/utils/domain/zone'
import { Optional } from '@/utils/typing'

export interface ZoneState extends ItemsState<Zone>{
  current: Optional<Zone>
  _loading: boolean
}

export interface RegionState {
  current: Optional<Region>
  use: boolean
  _loading: boolean
}
