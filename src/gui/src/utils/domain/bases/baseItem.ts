import { v4 as uuid } from 'uuid'

import { ID } from '@/utils/domain/types'
import { isUUID } from '@/utils/helpers'
import { Identifiable } from './interfaces'

export interface BaseItemConfiguration {
  id?: ID
}

export default class BaseItem implements Identifiable {
  public readonly id: ID
  public constructor ({ id }: BaseItemConfiguration = { id: undefined }) {
    if (!id) id = uuid()
    if (!isUUID(id)) throw TypeError('An item must have a valid UUID, as id')
    this.id = id
  }

  public toJSON () {
    // Include all (computed) properties, while dumping state to JSON
    // This makes reconstruction / population _much_ easier
    // Adapted from https://stackoverflow.com/a/50785428, and https://stackoverflow.com/a/8024294
    const jsonObj = Object.assign({}, this)
    let proto = this
    do {
      for (const key of Object.getOwnPropertyNames(proto)) {
        if (/__.*__/.exec(key)) continue
        const desc = Object.getOwnPropertyDescriptor(proto, key)
        const hasGetter = desc && typeof desc.get === 'function'
        if (hasGetter) {
          jsonObj[`${key}`] = this[`${key}`]
        }
      }
      // eslint-disable-next-line no-cond-assign
    } while (proto = Object.getPrototypeOf(proto))

    return jsonObj
  }
}