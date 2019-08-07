import ZoneRegionDependent, {
  DependentConfiguration,
  DependentSerialization
} from '@/utils/domain/bases/zoneRegionDependent'

export type CrossSectionType = 'IJ' | 'IK' | 'JK'

export interface CrossSectionConfiguration {
  type: CrossSectionType
}

type CrossSectionArgs = DependentConfiguration & CrossSectionConfiguration

export interface CrossSectionSerialization extends DependentSerialization {
  type: CrossSectionType
}

export default class CrossSection extends ZoneRegionDependent {
  public type: CrossSectionType

  public constructor ({ type, ...rest }: CrossSectionArgs) {
    super(rest)
    this.type = type
  }

  public toJSON (): CrossSectionSerialization {
    return {
      ...super.toJSON(),
      type: this.type,
    }
  }
}
