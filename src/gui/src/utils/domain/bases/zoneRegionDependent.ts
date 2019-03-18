import uuidv5 from 'uuid/v5'
import { isEmpty, getId } from '@/utils/helpers'
import Region from '@/utils/domain/region'
import { ID } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'
import BaseItem, { BaseItemConfiguration } from './baseItem'
import { Dependent, Parent } from './interfaces'

interface ParentConfiguration extends BaseItemConfiguration {
  zone?: null
  region?: null
  parent: Parent
}

interface ZoneRegionConfiguration extends BaseItemConfiguration {
  zone: Zone | string
  region?: Region | string | null
  parent?: { zone: null, region: null }
}

export type DependentConfiguration = ParentConfiguration | ZoneRegionConfiguration

// @ts-ignore
export function hasParents (item: any, zone, region): boolean {
  if (item.parent.zone === getId(zone)) {
    // The Zone ID is consistent
    if (region) {
      // We are dealing with a 'thing', that is SUPPOSED to have a region
      return item.parent.region === getId(region)
    } else {
      // The 'thing' should NOT have a region
      return !item.parent.region
    }
  } else {
    return false
  }
}

export default abstract class ZoneRegionDependent extends BaseItem implements Dependent {
  public readonly parent: Parent
  protected constructor ({
    id,
    zone,
    region = null,
    parent = { zone: null, region: null },
  }: DependentConfiguration) {
    super({ id })
    zone = zone || parent.zone
    region = region || parent.region
    zone = getId(zone)
    if (!zone) throw new Error('Missing \'zone\', or \'parent.zone\'')
    this.parent = {
      zone,
      region: isEmpty(region)
        ? null
        : (region instanceof Region) ? region.id : region,
    }
  }

  public isChildOf ({ zone, region = null }: Parent): boolean {
    return hasParents(this, zone, region)
  }

  public get parentId (): ID {
    if (this.parent.region) {
      return uuidv5(getId(this.parent.region), getId(this.parent.zone))
    } else {
      return getId(this.parent.zone)
    }
  }
}
