import _ from 'lodash'

export function isEmpty (property: any): boolean { return _.isEmpty(property) }
export function notEmpty (property: any): boolean { return !isEmpty(property) }

export function getRandomInt (max: number): number {
  return Math.floor(Math.random() * max)
}

export function newSeed (): number {
  return getRandomInt(Math.pow(2, 64) - 1)
}

export function allSet (items: any[], prop: string): boolean {
  return items
    ? Object.values(items).every((item): boolean => !!item[`${prop}`])
    : false
}