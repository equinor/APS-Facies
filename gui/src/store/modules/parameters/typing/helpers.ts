export interface Selectable<T=string> {
  selected: T | null
}

export interface SelectableChoice<T=string> extends Selectable<T> {
  available: T[]
}

export interface StaticChoices<T = string> {
  available: T[]
}
