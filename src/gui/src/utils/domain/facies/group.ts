import ZoneRegionDependent, { DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import Facies from '@/utils/domain/facies/local'
import { ID } from '@/utils/domain/types'
import { getId } from '@/utils/helpers'
import { checkFaciesId } from './helpers'

export default class FaciesGroup extends ZoneRegionDependent {
  public facies: Facies[]
  public constructor ({ facies, ...rest }: DependentConfiguration & { facies: Facies[]}) {
    super(rest)
    facies.forEach(facies => {
      checkFaciesId(facies)
    })
    this.facies = facies
  }

  public get length (): number { return this.facies.length }

  public has (facies: Facies): boolean {
    return new Set(this.facies.map(getId)).has(getId(facies))
  }

  public contains (facies: Facies[]): boolean {
    const collection: Set<ID> = new Set(facies.map(getId))
    return this.facies.filter(x => !collection.has(x.id)).length === 0
  }
}
