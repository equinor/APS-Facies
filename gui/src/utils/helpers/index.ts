import { v4 as uuidv4 } from 'uuid'
import { ID } from '@/utils/domain/types'
import { Identifiable, Identified } from '@/utils/domain/bases/interfaces'
import {
  allSet,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
} from '@/utils/helpers/simple'
import { NoCache } from '@/utils/helpers/decorators'

function isUUID (value: string): boolean {
  const uuid = /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/

  return RegExp(uuid).test(value)
}

function getId (item: any): ID | '' {
  if (isUUID(item)) return item
  if (item && isUUID(item.id)) return item.id
  return ''
}

type MaybeIdentified<T> = T & {
  id?: ID
}

type HasIdentity<T> = T & {
  id: ID
}

function identify<T> (items: MaybeIdentified<T>[] | Identified<MaybeIdentified<T>>): Identified<HasIdentity<T>> {
  return Object.values(items).reduce((obj, item): Identified<HasIdentity<T>> => {
    const _id = item.id || uuidv4()
    if (!('id' in item) || item.id !== _id) {
      item.id = _id
    }
    obj[`${_id}`] = (item as HasIdentity<T>)
    return obj
  }, ({} as Identified<HasIdentity<T>>))
}

function includes<T extends Identifiable> (items: T[], item: T | ID): boolean {
  return items.map(getId).includes(getId(item))
}

function hasOwnProperty<T> (obj: T, val: string): boolean {
  return Object.prototype.hasOwnProperty.call(obj, val)
}

export {
  isUUID,
  getId,
  identify,
  allSet,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
  includes,
  NoCache,
  hasOwnProperty,
}