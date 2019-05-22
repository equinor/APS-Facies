import BaseItem from '@/utils/domain/bases/baseItem'
import Facies from '@/utils/domain/facies/local'
import { ID, Identified, ORDER, PROBABILITY } from '@/utils/domain/types'
import { getFaciesName } from '@/utils/queries'

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

  public get atLevel (): number { return 0 }

  public get specification (): PolygonSpecification {
    return {
      facies: getFaciesName(this),
      fraction: this.fraction,
      order: this.order,
    }
}

export type Polygons = Identified<Polygon>
