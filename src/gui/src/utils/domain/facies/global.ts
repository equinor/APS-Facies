import Discrete, { DiscreteConfiguration, DiscreteSerialization } from '@/utils/domain/bases/discrete'
import { Color } from '@/utils/domain/facies/helpers/colors'

interface Configuration extends DiscreteConfiguration {
  color: Color
  alias?: string
}

export interface GlobalFaciesSerialization extends DiscreteSerialization {
  color: Color
  alias: string
}

export default class GlobalFacies extends Discrete {
  public color: Color
  public alias: string

  public constructor ({ alias, color, ...rest }: Configuration) {
    super(rest)
    this.color = color
    this.alias = alias || rest.name
  }

  public toJSON (): GlobalFaciesSerialization {
    return {
      ...super.toJSON(),
      color: this.color,
      alias: this.alias,
    }
  }
}
