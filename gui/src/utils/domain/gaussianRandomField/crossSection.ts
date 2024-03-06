import type {
  DependentConfiguration,
  DependentSerialization,
} from '@/utils/domain/bases/zoneRegionDependent'
import ZoneRegionDependent from '@/utils/domain/bases/zoneRegionDependent'

export type CrossSectionType = 'IJ' | 'IK' | 'JK'

export type CrossSectionConfiguration = DependentConfiguration & {
  type: CrossSectionType
}

export interface CrossSectionSerialization extends DependentSerialization {
  type: CrossSectionType
}

export class CrossSection extends ZoneRegionDependent {
  public type: CrossSectionType

  public constructor({ type, ...rest }: CrossSectionConfiguration) {
    super(rest)
    this.type = type
  }

  public toJSON(): CrossSectionSerialization {
    return {
      ...super.toJSON(),
      type: this.type,
    }
  }
}

export default CrossSection
