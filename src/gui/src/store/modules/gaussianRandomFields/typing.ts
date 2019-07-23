import { GaussianRandomField } from '@/utils/domain'
import { ItemsState } from '@/utils/domain/bases/baseItem'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'

export type CrossSectionsState = ItemsState<CrossSection>
export type GaussianRandomFieldState = ItemsState<GaussianRandomField>
