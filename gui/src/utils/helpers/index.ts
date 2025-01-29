import { v4 as uuidv4 } from 'uuid'
import type { ID } from '@/utils/domain/types'
import type { Identifiable, Identified } from '@/utils/domain/bases/interfaces'
import {
  allSet,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
} from '@/utils/helpers/simple'

function isUUID(value: unknown): value is ID {
  if (typeof value !== 'string') return false

  const uuid = /^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/
  return uuid.test(value)
}

function getId<T extends Identifiable>(
  item: T | ID | undefined | null,
): ID | '' {
  if (isUUID(item)) return item
  if (item && isUUID(item.id)) return item.id
  return ''
}

function identify<T extends Identifiable>(
  items: T[] | Identified<T>,
): Identified<T> {
  return Object.values(items).reduce((obj, item): Identified<T> => {
    const _id = item.id || uuidv4()
    if (!('id' in item) || item.id !== _id) {
      item.id = _id
    }
    obj[_id] = item
    return obj
  }, {} as Identified<T>)
}

function includes<T extends Identifiable>(items: T[], item: T | ID): boolean {
  return items.map(getId).includes(getId(item))
}

function hasOwnProperty<T, K extends keyof T | string>(
  obj: T,
  val: K,
): boolean {
  if (obj === null || obj === undefined) return false
  if (typeof obj !== 'object') return false
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
  hasOwnProperty,
}
