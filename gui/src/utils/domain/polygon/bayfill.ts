import type {
  FmuUpdatable,
} from '@/utils/domain/bases/fmuUpdatable'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import APSError from '@/utils/domain/errors/base'
import APSTypeError from '@/utils/domain/errors/type'
import type {
  PolygonArgs,
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import Polygon from '@/utils/domain/polygon/base'

export const SlantFactorFaciesValues = ['Floodplain', 'Subbay', 'Bayhead Delta'] as const
export const NonSlantFactorFaciesValues = ['Wave influenced Bayfill', 'Lagoon'] as const

export type SlantFactorFacies = typeof SlantFactorFaciesValues[number]

export type NonSlantFactorFacies = typeof NonSlantFactorFaciesValues[number]

export type BayfillFacies = SlantFactorFacies | NonSlantFactorFacies

export function hasBayfillName(name: string): name is BayfillFacies {
  return ([...SlantFactorFaciesValues, ...NonSlantFactorFaciesValues] as const).includes(name as BayfillFacies)
}

export type SlantFactorArgs = ({
  name: SlantFactorFacies
  slantFactor: FmuUpdatable | number
} | {
  name: NonSlantFactorFacies
  slantFactor?: null
})

export type BayfillPolygonArgs = PolygonArgs & SlantFactorArgs

type BayfillNameSpecification = 'SBHD' | 'SF' | 'YSF'

export interface BayfillPolygonSpecification extends PolygonSpecification {
  name: BayfillNameSpecification
  polygon: string
  factor: FmuUpdatable
}

export type BayfillPolygonSerialization = PolygonSerialization & SlantFactorArgs

export function requireSlantFactor(name: BayfillFacies): name is SlantFactorFacies {
  return (SlantFactorFaciesValues).includes(name as SlantFactorFacies)
}

export default class BayfillPolygon extends Polygon {
  public name: BayfillFacies
  public slantFactor: FmuUpdatable | null

  public constructor({
    name,
    slantFactor = null,
    ...rest
  }: BayfillPolygonArgs) {
    super(rest)
    this.name = name
    if (requireSlantFactor(name)) {
      if (slantFactor) {
        this.slantFactor = new FmuUpdatableValue(slantFactor)
      } else {
        throw new APSTypeError(
          `The Bayfill polygon, ${name} MUST have a slant factor`,
        )
      }
    }
  }

  public get isFmuUpdatable(): boolean {
    return (
      super.isFmuUpdatable ||
      (this.slantFactor !== null && this.slantFactor.updatable)
    )
  }

  public get specification(): BayfillPolygonSpecification {
    const _mapping: Record<string, BayfillNameSpecification> = {
      'Bayhead Delta': 'SBHD',
      Floodplain: 'SF',
      Subbay: 'YSF',
    }
    if (!Object.keys(_mapping).includes(this.name) || !this.slantFactor)
      throw new APSError(
        'A Bayfill polygon without a slant factor, CANNOT be used in a specification',
      )
    return {
      ...super.specification,
      name: _mapping[this.name],
      polygon: this.name,
      factor: this.slantFactor,
    }
  }

  public toJSON(): BayfillPolygonSerialization {
    return {
      ...super.toJSON(),
      ...({
        name: this.name,
        ...(this.slantFactor ? { slantFactor: this.slantFactor } : {}),
      } as SlantFactorArgs)
    }
  }
}
