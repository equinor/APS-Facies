import uuidv4 from 'uuid/v4'
import { ID, Identified } from '@/utils/domain/types'
import { Identifiable } from '@/utils/domain/bases/interfaces'
import {
  allSet,
  newSeed,
  getRandomInt,
  isEmpty,
  notEmpty,
} from '@/utils/helpers/simple'
import { NoCache } from '@/utils/helpers/decorators'

const hex = '[0-9a-f]'

function isUUID (value: string): boolean {
  const uuid = `${hex}{8}(-${hex}{4}){3}-${hex}{8}`

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

function identify<T extends object> (items: MaybeIdentified<T>[] | Identified<MaybeIdentified<T>>): Identified<HasIdentity<T>> {
  return Object.values(items).reduce((obj, item): Identified<HasIdentity<T>> => {
    const _id = item.id || uuidv4()
    if (!('id' in item) || item.id !== _id) {
      item.id = _id
    }
    obj[`${_id}`] = (item as HasIdentity<T>)
    return obj
  /* eslint-disable-next-line @typescript-eslint/no-object-literal-type-assertion */
  }, ({} as Identified<HasIdentity<T>>))
}

function includes<T extends Identifiable> (items: T[], item: T): boolean {
  return items.map(getId).includes(item.id)
}

function inDevelopmentMode (): boolean {
  return process.env.NODE_ENV === 'develop'
}

export {
  hex,
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
  inDevelopmentMode,
}
