import APSTypeError from '@/utils/domain/errors/type'

export interface FmuUpdatable<T extends number = number> {
  value: T
  updatable: boolean
}

export type MaybeFmuUpdatable<T extends number = number> = FmuUpdatable<T> | T

export type FmuUpdatableSerialization = FmuUpdatable

export default class FmuUpdatableValue<T extends number = number>
  implements FmuUpdatable
{
  public value: number
  public updatable: boolean

  public constructor(value: T | FmuUpdatable<T>, updatable = false) {
    if (value instanceof Object) {
      if ('updatable' in value) {
        updatable = (value as { updatable: boolean }).updatable
      }
      if (!('value' in value)) {
        throw new APSTypeError(
          "An object was passed, but does not contain 'value'",
        )
      } else {
        value = (value as { value: T }).value
      }
    }
    this.value = value
    this.updatable = updatable
  }

  public toJSON(): FmuUpdatableSerialization {
    return {
      value: this.value,
      updatable: this.updatable,
    }
  }

  public toString(): string {
    return `FmuUpdatable(${this.value}, ${this.updatable})`
  }
}
