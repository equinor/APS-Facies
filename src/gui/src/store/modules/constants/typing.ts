import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { Optional } from '@/utils/typing'

export interface ConstantsState {
  numberOf: {}
  faciesColors: StaticChoices<string>
  options: {
    variograms: StaticChoices<string>
    trends: StaticChoices<string>
    origin: StaticChoices<string>
  }
}

export interface MinMaxState {
  min: Optional<number>
  max: Optional<number>
}

export interface NumberOfGaussianRandomFieldsState {
  bayfill: MinMaxState
  nonCubic: MinMaxState
  cubic: MinMaxState
}
