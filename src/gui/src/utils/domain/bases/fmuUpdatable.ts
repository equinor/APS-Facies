import APSTypeError from '@/utils/domain/errors/type'

export interface FmuUpdatable {
  value: number
  updatable: boolean
}

export type FmuUpdatableSerialization = FmuUpdatable

export default class FmuUpdatableValue implements FmuUpdatable {
  public value: number
  public updatable: boolean

  public constructor (
    value: number | FmuUpdatable,
    updatable: boolean = false,
  ) {
    if (value instanceof Object) {
      if ('updatable' in (value as object)) {
        updatable = (value as { updatable: boolean}).updatable
      }
      if (!('value' in (value as object))) {
        throw new APSTypeError('An object was passed, but does not contain \'value\'')
      } else {
        value = (value as { value: number }).value
      }
    }
    this.value = value
    this.updatable = updatable
  }

  public toJSON (): FmuUpdatableSerialization {
    return {
      value: this.value,
      updatable: this.updatable,
    }
  }
}
