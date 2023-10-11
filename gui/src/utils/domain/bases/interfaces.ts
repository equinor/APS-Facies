import { Color } from '@/utils/domain/facies/helpers/colors'
import { CODE, ID } from '@/utils/domain/types'
import { Optional } from '@/utils/typing/simple'

export interface Newable<T> {
  new (...args: any[]): T
}

export interface Identifiable {
  id: ID
  [_: string]: any
}

export interface Selectable {
  selected: boolean | 'intermediate'
}

export interface Named {
  readonly name: string
}

export interface Coded {
  readonly code: CODE
}

export interface Discrete extends Named, Coded {}

export interface ParentReference {
  readonly zone: ID
  readonly region: ID | null
}

interface Coordinate2D {
  x: Optional<number>
  y: Optional<number>
}

export interface Coordinate3D extends Coordinate2D {
  z: Optional<number>
}

export interface SimulationSettings {
  gridAzimuth: Optional<number>
  gridSize: Coordinate3D
  simulationBox: Coordinate3D
  simulationBoxOrigin: Coordinate2D
}

export interface Ordered {
  order: number
}

export interface DialogOptions {
  color?: Color
  width?: number
}

export interface Identified<T> {
  [id: string]: T
}
