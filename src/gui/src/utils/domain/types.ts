export type ID = string
export type CODE = number

export type ORDER = number
export type FRACTION = number
export type PROBABILITY = FRACTION

export interface Identified<T> {
  [id: string]: T
}