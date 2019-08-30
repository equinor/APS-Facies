import _ from 'lodash'

import { ERROR_TOLERENCE } from '@/config'

export function isEmpty (property: any): boolean { return _.isEmpty(property) && !_.isNumber(property) }
export function notEmpty (property: any): boolean { return !isEmpty(property) }

export function getRandomInt (max: number): number {
  return Math.floor(Math.random() * max)
}

export function newSeed (): number {
  return getRandomInt(Math.pow(2, 64) - 1)
}

export function allSet<T> (items: T[], prop: string): boolean {
  return items
    ? Object.values(items).every((item): boolean => !!item[`${prop}`])
    : false
}

export function isCloseTo (val: number, target: number): boolean {
  // Since JavaScript uses floats, there are times when comparing against 1 (or another number) will fail
  // because of a rounding error
  return Math.abs(val - target) <= ERROR_TOLERENCE
}

export function isCloseToUnity (val: number): boolean {
  return isCloseTo(val, 1)
}
