import FmuUpdatableValue, { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import APSTypeError from '@/utils/domain/errors/type'
import Polygon, { PolygonArgs } from '@/utils/domain/polygon/base'

enum SlantFactorFacies {
  Floodplain = 'Floodplain',
  Subbay = 'Subbay',
  BayheadDelta = 'Bayhead Delta',
}

const enum NonSlantFactorFacies {
  WaveInfluencedBayfill = 'Wave influenced Bayfill',
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
    if (Object.values(SlantFactorFacies).includes(name)) {
      if (slantFactor) {
        this.slantFactor = new FmuUpdatableValue(slantFactor)
      } else {
        throw new APSTypeError(`The Bayfill polygon, ${name} MUST have a slant factor`)
      }
    }
  }
}
