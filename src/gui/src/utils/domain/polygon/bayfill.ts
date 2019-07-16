import FmuUpdatableValue, { FmuUpdatable } from '@/utils/domain/bases/fmuUpdatable'
import APSError from '@/utils/domain/errors/base'
import APSTypeError from '@/utils/domain/errors/type'
import Polygon, { PolygonArgs, PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'

enum SlantFactorFacies {
  Floodplain = 'Floodplain',
  Subbay = 'Subbay',
  BayheadDelta = 'Bayhead Delta',
}

export interface BayfillPolygonArgs extends PolygonArgs {
  name: BayfillFacies | string
  slantFactor: FmuUpdatable | number | null
}

const enum NonSlantFactorFacies {
  WaveInfluencedBayfill = 'Wave influenced Bayfill',
  Lagoon = 'Lagoon',
}
type BayfillFacies = SlantFactorFacies | NonSlantFactorFacies

export interface BayfillPolygonSpecification extends PolygonSpecification {
  name: string
  polygon: string
  factor: FmuUpdatable
}

export interface BayfillPolygonSerialization extends PolygonSerialization {
  name: BayfillFacies | string
  slantFactor?: FmuUpdatable
}

export default class BayfillPolygon extends Polygon {
  public name: BayfillFacies | string
  public slantFactor: FmuUpdatable | null

  public constructor ({ name, slantFactor = null, ...rest }: BayfillPolygonArgs) {
    super(rest)
    this.name = name
    // @ts-ignore
    if (Object.values(SlantFactorFacies).includes(name)) {
      if (slantFactor) {
        this.slantFactor = new FmuUpdatableValue(slantFactor)
      } else {
        throw new APSTypeError(`The Bayfill polygon, ${name} MUST have a slant factor`)
      }
    }
  }

  public get specification (): BayfillPolygonSpecification {
    const _mapping: {[_: string]: string} = {
      'Bayhead Delta': 'SBHD',
      'Floodplain': 'SF',
      'Subbay': 'YSF',
    }
    if (!Object.keys(_mapping).includes(this.name) || !this.slantFactor) throw new APSError('A Bayfill polygon without a slant factor, CANNOT be used in a specification')
    return {
      ...super.specification,
      name: _mapping[this.name],
      polygon: this.name,
      factor: this.slantFactor,
    }
  }

  public toJSON (): BayfillPolygonSerialization {
    return {
      ...super.toJSON(),
      name: this.name,
      ...(this.slantFactor ? { slantFactor: this.slantFactor } : {})
    }
  }
}
