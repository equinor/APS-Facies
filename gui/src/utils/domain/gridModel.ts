import type {
  BaseItemConfiguration,
  BaseItemSerialization,
} from '@/utils/domain/bases/baseItem'
import BaseItem from '@/utils/domain/bases/baseItem'

export interface Dimension {
  x: number
  y: number
  z: number
}

export interface GridModelConfiguration extends BaseItemConfiguration {
  name: string
  order: number
  exists: boolean
  dimension: Dimension
  zones: number
  hasDualIndexSystem: boolean
}

export interface GridModelSerialization extends BaseItemSerialization {
  name: string
  order: number
  exists: boolean
  dimension: Dimension
  zones: number
  hasDualIndexSystem: boolean
}

export default class GridModel extends BaseItem {
  public readonly name: string
  public readonly order: number
  public readonly exists: boolean
  public readonly dimension: Dimension
  public readonly zones: number
  public readonly hasDualIndexSystem: boolean

  public constructor({
    name,
    order,
    dimension,
    zones,
    hasDualIndexSystem,
    exists = true,
    ...rest
  }: GridModelConfiguration) {
    super(rest)
    this.name = name
    this.exists = exists
    this.order = order
    this.dimension = dimension
    this.zones = zones
    this.hasDualIndexSystem = hasDualIndexSystem
  }

  public toJSON(): GridModelSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      order: this.order,
      exists: this.exists,
      dimension: this.dimension,
      zones: this.zones,
      hasDualIndexSystem: this.hasDualIndexSystem,
    }
  }
}
