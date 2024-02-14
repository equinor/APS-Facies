import type {
  DiscreteConfiguration,
  DiscreteSerialization,
} from './discrete'
import Discrete from './discrete'
import type { Selectable } from './interfaces'

export type SelectedType = boolean | 'intermediate'

export interface SelectableItemConfiguration extends DiscreteConfiguration {
  selected?: SelectedType
  touched?: boolean
}

export interface SelectableSerialization extends DiscreteSerialization {
  selected: SelectedType
  touched: boolean
}

export default class SelectableItem extends Discrete implements Selectable {
  protected _selected: SelectedType
  protected _touched: boolean

  public constructor({
    selected = false,
    touched = false,
    ...rest
  }: SelectableItemConfiguration) {
    super(rest)
    this.selected = selected
    this._touched = touched
  }

  public get touched(): boolean {
    return this._touched
  }
  public touch(): void {
    this._touched = true
  }

  public get selected(): SelectedType {
    return this._selected
  }
  public set selected(toggled: SelectedType) {
    this._selected = toggled
  }

  protected toJSON(): SelectableSerialization {
    return {
      ...super.toJSON(),
      touched: this.touched,
      selected: this.selected,
    }
  }
}
