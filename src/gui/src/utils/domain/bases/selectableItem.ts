import { BaseItemConfiguration } from '@/utils/domain/bases/baseItem'
import Discrete, { DiscreteSerialization } from './discrete'
import { Discrete as IDiscrete, Selectable } from './interfaces'

type SelectedType = boolean | 'intermediate'

export interface SelectableItemConfiguration extends IDiscrete, BaseItemConfiguration {
  selected?: SelectedType
}

export interface SelectableSerialization extends DiscreteSerialization {
  selected: SelectedType
}

export default class SelectableItem extends Discrete implements Selectable {
  public selected: SelectedType

  public constructor ({ selected = false, ...rest }: SelectableItemConfiguration) {
    super(rest)
    this.selected = selected
  }

  protected toJSON (): SelectableSerialization {
    return {
      ...super.toJSON(),
      selected: this.selected,
    }
  }
}
