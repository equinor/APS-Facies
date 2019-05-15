export enum Orientation {
  'VERTICAL',
  'HORIZONTAL',
}

export default class Direction {
  public readonly orientation: Orientation

  public constructor (direction: Orientation | Direction) {
    if (direction instanceof Direction) {
      direction = direction.orientation
    }
    this.orientation = direction
  }

  public get label (): string {
    return this.orientation === Orientation.VERTICAL
      ? 'Vertical'
      : 'Horizontal'
  }

  public get specification (): 'V' | 'H' {
    return this.orientation === Orientation.VERTICAL ? 'V' : 'H'
  }

  public toString (): 'V' | 'H' {
    return this.specification
  }

  public toInteger (): 0 | 1 {
    return this.orientation === Orientation.VERTICAL
      ? 0
      : 1
  }
}
