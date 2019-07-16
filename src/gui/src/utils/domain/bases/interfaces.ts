import { Color } from '@/utils/domain/facies/helpers/colors'
import { CODE, ID } from '@/utils/domain/types'

export interface Identifiable {
  id: ID
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

export interface Discrete extends Named, Coded {
}

export interface Parent {
  readonly zone: ID
  readonly region: ID | null
}

export interface Dependent {
  readonly parent: Parent
  isChildOf (parent: Parent): boolean
}

interface Coordinate2D {
  x: number
  y: number
}

interface Coordinate3D extends Coordinate2D {
  z: number
}

export interface SimulationSettings {
  gridAzimuth: number
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
