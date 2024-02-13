import _ from 'lodash'

import { ERROR_TOLERANCE, isDevelopmentBuild } from '@/config'

export function isEmpty<T>(
  property: T | null | undefined,
): property is null | undefined {
  return _.isEmpty(property) && !_.isNumber(property)
}
export function notEmpty<T>(property: T | null | undefined): property is T {
  return !isEmpty(property)
}

export function getRandomInt(max: number): number {
  return Math.floor(Math.random() * max)
}

export function newSeed(): number {
  return getRandomInt(Math.pow(2, 64) - 1)
}

export function allSet<T, K extends keyof T>(items: T[], prop: K): boolean {
  return items?.every((item): boolean => !!item[prop]) ?? false
}

export function isCloseTo(val: number, target: number): boolean {
  // Since JavaScript uses floats, there are times when comparing against 1 (or another number) will fail
  // because of a rounding error
  return Math.abs(val - target) <= ERROR_TOLERANCE
}

export function isCloseToUnity(val: number): boolean {
  return isCloseTo(val, 1)
}

export function getDisabledOpacity(disabled: boolean): number {
  // TODO weird to use this decimal value, even if it equals 66/255...?
  // why not just use 0.25, surely noone can tell the difference?
  return disabled ? 0.258823529 : 1
}

export { isDevelopmentBuild }
