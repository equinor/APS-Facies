import { v5 as uuidv5 } from 'uuid'
import { getId } from '@/utils/helpers'
import Region from '@/utils/domain/region'
import { ID } from '@/utils/domain/types'
import Zone from '@/utils/domain/zone'
import BaseItem, {
  BaseItemConfiguration,
  BaseItemSerialization,
} from './baseItem'
import { ParentReference } from './interfaces'
import { Optional } from '@/utils/typing'

export interface Parent {
  zone: Zone
  region: Optional<Region>
}

interface ParentConfiguration extends BaseItemConfiguration {
  zone?: never
  region?: never
  parent: Parent
}

interface ZoneRegionConfiguration extends BaseItemConfiguration {
  zone: Zone
  region: Optional<Region>
  parent?: never
}

export type DependentConfiguration =
  | ParentConfiguration
  | ZoneRegionConfiguration

export interface DependentSerialization extends BaseItemSerialization {
  parent: ParentReference
}

export interface Dependent {
  readonly parent: Parent
  isChildOf(parent: Parent | ParentReference): boolean
}

export function hasParents<T extends Dependent>(
  item: T,
  zone: Zone | ID,
  region: Region | ID | null,
): boolean {
  if (getId(item.parent.zone) === getId(zone)) {
    // The Zone ID is consistent
    if (region) {
      // We are dealing with a 'thing', that is SUPPOSED to have a region
      return getId(item.parent.region) === getId(region)
    } else {
      // The 'thing' should NOT have a region
      return !item.parent.region
    }
  } else {
    return false
  }
}

export function getParentId(parent: Parent | ParentReference): ID {
  return uuidv5(getId(parent.region), getId(parent.zone))
}

export default abstract class ZoneRegionDependent
  extends BaseItem
  implements Dependent
{
  public readonly parent: Parent

  protected constructor({
    id,
    zone,
    region = null,
    parent,
  }: DependentConfiguration) {
    super({ id })
    zone = zone || parent.zone
    region = region ?? parent?.region ?? null
    if (!zone) throw new Error("Missing 'zone', or 'parent.zone'")
    this.parent = {
      zone,
      region,
    }
  }

  public get parentReference(): ParentReference {
    return {
      zone: getId(this.parent.zone),
      region: getId(this.parent.region) || null,
    }
  }

  public isChildOf({ zone, region = null }: Parent | ParentReference): boolean {
    return hasParents(this, zone, region)
  }

  public get parentId(): ID {
    if (this.parent.region) {
      return getParentId(this.parent)
    } else {
      return getId(this.parent.zone)
    }
  }

  protected toJSON(): DependentSerialization {
    return {
      ...super.toJSON(),
      parent: this.parentReference,
    }
  }
}
