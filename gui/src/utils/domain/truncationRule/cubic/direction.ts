export enum Orientation {
  'VERTICAL',
  'HORIZONTAL',
}

export type OrientationString = 'V' | 'H'

export default class Direction {
  public readonly orientation: Orientation

  public constructor(direction: Orientation | Direction | OrientationString) {
    if (direction instanceof Direction) {
      direction = direction.orientation
    } else if (direction === 'V') {
      direction = Orientation.VERTICAL
    } else if (direction === 'H') {
      direction = Orientation.HORIZONTAL
    }
    this.orientation = direction
  }

  public get label(): string {
    return this.orientation === Orientation.VERTICAL ? 'Vertical' : 'Horizontal'
  }

  public get specification(): OrientationString {
    return this.orientation === Orientation.VERTICAL ? 'V' : 'H'
  }

  public toString(): OrientationString {
    return this.specification
  }

  public toInteger(): 0 | 1 {
    return this.orientation === Orientation.VERTICAL ? 0 : 1
  }
}
