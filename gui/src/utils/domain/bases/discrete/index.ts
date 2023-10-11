import CodeError from '@/utils/domain/bases/discrete/codeError'
import { APSTypeError } from '@/utils/domain/errors'
import { CODE, ID } from '@/utils/domain/types'
import { isInteger } from 'lodash'
import BaseItem, {
  BaseItemConfiguration,
  BaseItemSerialization,
} from '../baseItem'
import { Discrete as IDiscrete } from '../interfaces'

export interface DiscreteSerialization extends BaseItemSerialization {
  name: string
  code: number
}

export interface DiscreteConfiguration
  extends IDiscrete,
    BaseItemConfiguration {}

export default class Discrete extends BaseItem implements IDiscrete {
  public readonly name: string
  public readonly code: CODE

  protected constructor({
    id,
    name,
    code,
  }: {
    id?: ID | undefined
    name: string
    code: CODE
  }) {
    super({ id })
    this.name = name
    if (!isInteger(code))
      throw new APSTypeError(
        `A discrete item MUST have an integer as code. Was ${code}`,
      )
    if (code < 0) throw new CodeError(code)
    this.code = code
  }

  protected toJSON(): DiscreteSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      code: this.code,
    }
  }

  protected toString(): string {
    return `${this.constructor.name}(name='${this.name}', code=${this.code})`
  }
}
