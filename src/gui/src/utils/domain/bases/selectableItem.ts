import Discrete, { DiscreteConfiguration, DiscreteSerialization } from './discrete'
import { Selectable } from './interfaces'

export type SelectedType = boolean | 'intermediate'

export interface SelectableItemConfiguration extends DiscreteConfiguration {
  selected?: SelectedType
}

export interface SelectableSerialization extends DiscreteSerialization {
  selected: SelectedType
}

export default class SelectableItem extends Discrete implements Selectable {
  protected _selected: SelectedType

  public constructor ({ selected = false, ...rest }: SelectableItemConfiguration) {
    super(rest)
    this.selected = selected
  }

  public get selected (): SelectedType { return this._selected }
  public set selected (toggled: SelectedType) { this._selected = toggled }

  protected toJSON (): SelectableSerialization {
    return {
      ...super.toJSON(),
      selected: this.selected,
    }
  }
}
