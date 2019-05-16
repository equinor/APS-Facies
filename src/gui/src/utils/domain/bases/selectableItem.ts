import { BaseItemConfiguration } from '@/utils/domain/bases/baseItem'
import Discrete from './discrete'
import { Discrete as IDiscrete, Selectable } from './interfaces'

export interface SelectableItemConfiguration extends IDiscrete, BaseItemConfiguration {
  selected?: boolean | 'intermediate'
}

export default class SelectableItem extends Discrete implements Selectable {
  public selected: 'intermediate' | boolean

  public constructor ({ selected = false, ...rest }: SelectableItemConfiguration) {
    super(rest)
    this.selected = selected
  }
}
