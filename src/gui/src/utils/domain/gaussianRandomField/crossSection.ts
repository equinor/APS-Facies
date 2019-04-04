import ZoneRegionDependent, { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'

export type CrossSectionType = 'IJ' | 'IK' | 'JK'

export interface CrossSectionConfiguration {
  type: CrossSectionType
  relativePosition: number
}

type CrossSectionArgs = DependentConfiguration & CrossSectionConfiguration

export default class CrossSection extends ZoneRegionDependent {
  public type: CrossSectionType
  public relativePosition: number

  public constructor ({ type, relativePosition, ...rest }: CrossSectionArgs) {
    super(rest)
    this.type = type
    this.relativePosition = relativePosition
  }
}
