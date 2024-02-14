import type {
  DependentConfiguration,
  DependentSerialization,
} from '@/utils/domain/bases/zoneRegionDependent'
import ZoneRegionDependent from '@/utils/domain/bases/zoneRegionDependent'
import type Facies from '@/utils/domain/facies/local'
import type { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'
import { checkFaciesId } from './helpers'

export interface FaciesGroupSerialization extends DependentSerialization {
  facies: ID[]
}

export type FaciesGroupConfiguration = DependentConfiguration & {
  facies: Facies[]
}

export default class FaciesGroup extends ZoneRegionDependent {
  public facies: Facies[]

  public constructor({ facies, ...rest }: FaciesGroupConfiguration) {
    super(rest)
    facies.forEach((facies): void => {
      checkFaciesId(facies)
    })
    this.facies = facies
  }

  public get length(): number {
    return this.facies.length
  }

  public has(facies: Facies): boolean {
    return new Set(this.facies.map(getId)).has(getId(facies))
  }

  public contains(facies: Facies[]): boolean {
    const collection: Set<ID> = new Set(facies.map(getId))
    return this.facies.filter((x) => !collection.has(x.id)).length === 0
  }

  public toJSON(): FaciesGroupSerialization {
    return {
      ...super.toJSON(),
      facies: this.facies.map(({ id }): ID => id),
    }
  }
}
