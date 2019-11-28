import BaseItem, { BaseItemConfiguration, BaseItemSerialization } from '@/utils/domain/bases/baseItem'

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
}

export interface GridModelSerialization extends BaseItemSerialization {
  name: string
  order: number
  exists: boolean
  dimension: Dimension
}

export default class GridModel extends BaseItem {
  public readonly name: string
  public readonly order: number
  public readonly exists: boolean
  public readonly dimension: Dimension

  public constructor ({ name, order, dimension, exists = true, ...rest }: GridModelConfiguration) {
    super(rest)
    this.name = name
    this.exists = exists
    this.order = order
    this.dimension = dimension
  }

  public toJSON (): GridModelSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      order: this.order,
      exists: this.exists,
      dimension: this.dimension,
    }
  }
}
