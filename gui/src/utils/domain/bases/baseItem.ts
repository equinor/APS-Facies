import { v4 as uuid } from 'uuid'
import hash from 'object-hash'

import type { ID } from '@/utils/domain/types'
import { isUUID } from '@/utils/helpers'
import type { Identifiable, Identified } from './interfaces'

export interface BaseItemSerialization {
  id: ID
}

export interface BaseItemConfiguration {
  id?: ID
}

export default class BaseItem implements Identifiable {
  public readonly id: ID
  protected readonly _excludeFromHash: string[]

  public constructor({ id }: BaseItemConfiguration = { id: undefined }) {
    if (!id) id = uuid()
    if (!isUUID(id)) throw TypeError('An item must have a valid UUID, as id')
    this.id = id
    this._excludeFromHash = []
  }

  protected toJSON(): BaseItemSerialization {
    return {
      id: this.id,
    }
  }

  protected _hashify(): any {
    return this.toJSON()
  }

  protected get hash(): string {
    return hash(this._hashify(), {
      excludeKeys: (key): boolean => this._excludeFromHash.includes(key),
    })
  }
}

export interface ItemsState<T extends BaseItem> {
  available: Identified<T>
}
