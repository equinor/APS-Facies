import { CODE, ID } from '@/utils/domain/types'

export interface Identifiable {
  id: ID
}

export interface Selectable {
  selected: boolean
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
  readonly zone: string
  readonly region: string | null
}

export interface Dependent {
  readonly parent: Parent
  isChildOf (parent: Parent): boolean
}
