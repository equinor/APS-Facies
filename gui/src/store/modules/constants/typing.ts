import { StaticChoices } from '@/store/modules/parameters/typing/helpers'
import { Identified } from '@/utils/domain/bases/interfaces'
import ColorLibrary from '@/utils/domain/colorLibrary'
import { ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing'

export interface ConstantsState {
  numberOf: Record<string, number>
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

export interface FaciesColorsState {
  available: Identified<ColorLibrary>
  current: ID
}
