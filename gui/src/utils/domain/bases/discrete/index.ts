import CodeError from '@/utils/domain/bases/discrete/codeError'
import { APSTypeError } from '@/utils/domain/errors'
import type { CODE, ID } from '@/utils/domain/types'
import { isInteger } from 'lodash'
import BaseItem, {
  type BaseItemConfiguration,
  type BaseItemSerialization,
} from '@/utils/domain/bases/baseItem'
import type { Discrete as IDiscrete } from '@/utils/domain/bases/interfaces'

export interface DiscreteSerialization extends BaseItemSerialization {
  name: string
  code: number
}

export interface DiscreteConfiguration
  extends IDiscrete,
    BaseItemConfiguration {}

export class Discrete extends BaseItem implements IDiscrete {
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

export default Discrete
