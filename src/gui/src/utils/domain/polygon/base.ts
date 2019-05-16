import BaseItem from '@/utils/domain/bases/baseItem'
import Facies from '@/utils/domain/facies/local'
import { ID, Identified, ORDER, PROBABILITY } from '@/utils/domain/types'

export interface PolygonArgs {
  id?: ID
  order: ORDER
  fraction?: PROBABILITY
  facies?: Facies | null
}

export interface PolygonSpecification {
  facies: string
  fraction: PROBABILITY
  order: number
}

export default abstract class Polygon extends BaseItem {
  public order: ORDER
  public fraction: PROBABILITY
  public facies: Facies | null

  protected constructor ({ id, order, facies = null, fraction = 1.0 }: PolygonArgs) {
    super({ id })
    this.order = order
    this.facies = facies
    this.fraction = fraction
  }

  public get overlay (): boolean { return false }
}

export type Polygons = Identified<Polygon>
