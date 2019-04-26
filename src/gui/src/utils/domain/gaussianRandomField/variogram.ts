import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

interface Angle {
  azimuth: FmuUpdatableValue
  dip: FmuUpdatableValue
}

interface Range {
  main: FmuUpdatableValue
  perpendicular: FmuUpdatableValue
  vertical: FmuUpdatableValue
}

export default class Variogram {
  public type: string
  public angle: Angle
  public range: Range
  public power: FmuUpdatableValue

  public constructor ({
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
    power = 1.5,
    verticalUpdatable = false,
    powerUpdatable = false,
  }) {
    this.type = type
    this.angle = {
      azimuth: new FmuUpdatableValue(azimuth, !!azimuthUpdatable),
      dip: new FmuUpdatableValue(dip, !!dipUpdatable),
    }
    this.range = {
      main: new FmuUpdatableValue(main, !!mainUpdatable),
      perpendicular: new FmuUpdatableValue(perpendicular, !!perpendicularUpdatable),
      vertical: new FmuUpdatableValue(vertical, !!verticalUpdatable),
    }
    this.power = new FmuUpdatableValue(power, !!powerUpdatable)
  }
}
