import FmuUpdatableValue, { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import Polygon, { PolygonArgs } from '@/utils/domain/polygon/base'

const enum SlantFactorFacies {
  Floodplain = 'Floodplain',
  Subbay = 'Subbay',
  BayheadDelta = 'Wave influenced Bayfill',
}

const enum NonSlantFactorFacies {
  WaveInfluencedBayfill = 'Bayhead Delta',
  Lagoon = 'Lagoon',
}
type BayfillFacies = SlantFactorFacies | NonSlantFactorFacies

export default class BayfillPolygon extends Polygon {
  public name: BayfillFacies | string
  public slantFactor: FmuUpdatable | null
  public constructor ({ name, slantFactor = null, ...rest }: PolygonArgs & {
    name: BayfillFacies | string
    slantFactor: FmuUpdatable | number | null
  }) {
    super(rest)
    this.name = name
    this.slantFactor = slantFactor ? new FmuUpdatableValue(slantFactor) : null // TODO: Check type / name
  }
}
