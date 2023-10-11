import BaseItem from '@/utils/domain/bases/baseItem'
import { Identified, Ordered } from '@/utils/domain/bases/interfaces'
import Facies from '@/utils/domain/facies/local'
import { ID, ORDER, PROBABILITY } from '@/utils/domain/types'

export function getFaciesName(polygon: Polygon): string {
  return polygon.facies ? polygon.facies.name : ''
}

interface BasePolygonSpec<F> {
  id?: ID
  facies?: F
  fraction?: PROBABILITY
  order: ORDER
}

export type PolygonArgs = BasePolygonSpec<Facies | null>

export interface PolygonSpecification extends BasePolygonSpec<string> {
  facies: string
  fraction: PROBABILITY
}

export interface PolygonSerialization extends BasePolygonSpec<ID | null> {
  id: ID
  facies: ID | null
  fraction: PROBABILITY
  overlay: boolean
}

export default abstract class Polygon extends BaseItem implements Ordered {
  public order: ORDER
  public fraction: PROBABILITY
  public facies: Facies | null

  protected constructor({
    order,
    facies = null,
    fraction = 1.0,
    ...rest
  }: PolygonArgs) {
    super(rest)
    this.order = order
    this.facies = facies
    this.fraction = fraction
  }

  public get overlay(): boolean {
    return false
  }

  public get atLevel(): number {
    return 0
  }

  public get specification(): PolygonSpecification {
    return {
      facies: getFaciesName(this),
      fraction: this.fraction,
      order: this.order,
    }
  }

  public get isFmuUpdatable(): boolean {
    return false
  }

  public toJSON(): PolygonSerialization {
    return {
      id: this.id,
      facies: this.facies ? this.facies.id : null,
      fraction: this.fraction,
      order: this.order,
      overlay: this.overlay,
    }
  }
}

export type Polygons = Identified<Polygon>
