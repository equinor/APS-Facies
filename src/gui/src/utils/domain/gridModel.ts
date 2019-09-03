import BaseItem, { BaseItemConfiguration, BaseItemSerialization } from '@/utils/domain/bases/baseItem'

export interface GridModelConfiguration extends BaseItemConfiguration {
  name: string
  order: number
  exists: boolean
}

export interface GridModelSerialization extends BaseItemSerialization {
  name: string
  order: number
  exists: boolean
}

// TODO: Order
export default class GridModel extends BaseItem {
  public readonly name: string
  public readonly order: number
  public readonly exists: boolean

  public constructor ({ name, order, exists = true, ...rest }: GridModelConfiguration) {
    super(rest)
    this.name = name
    this.exists = exists
    this.order = order
  }

  public toJSON (): GridModelSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      order: this.order,
      exists: this.exists,
    }
  }
}
