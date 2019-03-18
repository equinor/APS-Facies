import Discrete from '@/utils/domain/bases/discrete'
import { Discrete as IDiscrete } from '@/utils/domain/bases/interfaces'
import { Color } from '@/utils/domain/facies/helpers/colors'

interface Configuration extends IDiscrete {
  color: Color
  alias?: string
}

export default class GlobalFacies extends Discrete {
  public color: Color
  public alias: string
  public constructor ({ alias, color, ...rest }: Configuration) {
    super(rest)
    this.color = color
    this.alias = alias || rest.name
  }
}
