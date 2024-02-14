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

  // eslint-disable-next-line no-use-before-define
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

  protected objectify(): { [_: string]: any } {
    // Include all (computed) properties, while dumping state to JSON
    // This makes reconstruction / population _much_ easier
    // Adapted from https://stackoverflow.com/a/50785428, and https://stackoverflow.com/a/8024294
    const jsonObj = Object.assign({}, this)
    // eslint-disable-next-line @typescript-eslint/no-this-alias
    let proto = this
    do {
      for (const key of Object.getOwnPropertyNames(proto)) {
        if (/__.*__/.exec(key)) continue
        const desc = Object.getOwnPropertyDescriptor(proto, key)
        const hasGetter = desc && typeof desc.get === 'function'
        if (hasGetter) {
          jsonObj[key] = this[key]
        }
      }
      // eslint-disable-next-line no-cond-assign
    } while ((proto = Object.getPrototypeOf(proto)))

    return jsonObj
  }
}

export interface ItemsState<T extends BaseItem> {
  available: Identified<T>
}
