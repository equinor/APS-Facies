import type {
  FmuUpdatableSerialization,
} from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

interface Angle {
  azimuth: FmuUpdatableValue
  dip: FmuUpdatableValue
}

interface AngleSerialization {
  azimuth: FmuUpdatableSerialization
  dip: FmuUpdatableSerialization
}

interface Range {
  main: FmuUpdatableValue
  perpendicular: FmuUpdatableValue
  vertical: FmuUpdatableValue
}

interface RangeSerialization {
  main: FmuUpdatableSerialization
  perpendicular: FmuUpdatableSerialization
  vertical: FmuUpdatableSerialization
}

type VariogramType = string

export interface VariogramConfiguration {
  type?: VariogramType
  azimuth?: number
  azimuthUpdatable?: boolean
  dip?: number
  dipUpdatable?: boolean
  main?: number
  mainUpdatable?: boolean
  perpendicular?: number
  perpendicularUpdatable?: boolean
  vertical?: number
  verticalUpdatable?: boolean
  power?: number
  powerUpdatable?: boolean
}

export interface VariogramSerialization {
  type: VariogramType
  angle: AngleSerialization
  range: RangeSerialization
  power: FmuUpdatableSerialization
}

export function unpackVariogram(
  variogram: VariogramSerialization,
): VariogramConfiguration {
  return {
    type: variogram.type,
    azimuth: variogram.angle.azimuth.value,
    azimuthUpdatable: variogram.angle.azimuth.updatable,
    dip: variogram.angle.dip.value,
    dipUpdatable: variogram.angle.dip.updatable,
    main: variogram.range.main.value,
    mainUpdatable: variogram.range.main.updatable,
    perpendicular: variogram.range.perpendicular.value,
    perpendicularUpdatable: variogram.range.perpendicular.updatable,
    vertical: variogram.range.vertical.value,
    verticalUpdatable: variogram.range.vertical.updatable,
    power: variogram.power.value,
    powerUpdatable: variogram.power.updatable,
  }
}

export default class Variogram {
  public type: string
  public angle: Angle
  public range: Range
  public power: FmuUpdatableValue

  public constructor({
    type = 'SPHERICAL',
    // Angles
    azimuth = 0,
    azimuthUpdatable = false,
    dip = 0,
    dipUpdatable = false,
    // Ranges
    main = 1000,
    mainUpdatable = false,
    perpendicular = 1000,
    perpendicularUpdatable = false,
    vertical = 5,
    verticalUpdatable = false,
    power = 1.5,
    powerUpdatable = false,
  }: VariogramConfiguration) {
    this.type = type
    this.angle = {
      azimuth: new FmuUpdatableValue(azimuth, !!azimuthUpdatable),
      dip: new FmuUpdatableValue(dip, !!dipUpdatable),
    }
    this.range = {
      main: new FmuUpdatableValue(main, !!mainUpdatable),
      perpendicular: new FmuUpdatableValue(
        perpendicular,
        !!perpendicularUpdatable,
      ),
      vertical: new FmuUpdatableValue(vertical, !!verticalUpdatable),
    }
    this.power = new FmuUpdatableValue(power, !!powerUpdatable)
  }

  public get isFmuUpdatable(): boolean {
    return (
      this.angle.azimuth.updatable ||
      this.angle.dip.updatable ||
      this.range.main.updatable ||
      this.range.perpendicular.updatable ||
      this.range.vertical.updatable ||
      (this.type === 'GENERAL_EXPONENTIAL' && this.power.updatable)
    )
  }

  public toJSON(): VariogramSerialization {
    return {
      type: this.type,
      angle: this.angle,
      range: this.range,
      power: this.power,
    }
  }
}
