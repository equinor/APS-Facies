import { Identified } from '@/utils/domain/bases/interfaces'
import { ID } from '@/utils/domain/types'
import { identify } from '@/utils/helpers'
import SelectableItem, {
  SelectableItemConfiguration,
  SelectableSerialization,
  SelectedType,
} from './bases/selectableItem'

type Regions = Identified<Region>

export type ZoneConformOption = 'top' | 'bottom' | 'proportional' | null

export interface ZoneSerialization extends SelectableSerialization {
  regions: RegionSerialization[] | null
  conformity: ZoneConformOption
  thickness: number
}

export interface RegionSerialization extends SelectableSerialization {
  zone: ID
}

export interface RegionConfiguration extends SelectableItemConfiguration {
  zone: Zone
}

export class Region extends SelectableItem {
  public readonly zone: Zone

  public constructor ({ zone, ...rest }: RegionConfiguration) {
    super(rest)
    this.zone = zone
  }

  public touch (): void {
    super.touch()
    this.zone.touch()
  }

  public toJSON (): RegionSerialization {
    return {
      ...super.toJSON(),
      zone: this.zone.id,
    }
  }
}

export interface ZoneConfiguration extends SelectableItemConfiguration {
  thickness: number
  regions?: Region[] | null
  conformity?: ZoneConformOption
}

export default class Zone extends SelectableItem {
  private _regions: Regions
  public readonly thickness: number
  public conformity: ZoneConformOption

  public constructor ({
    thickness,
    regions = null,
    conformity = null,
    ...rest
  }: ZoneConfiguration) {
    super(rest)
    this.thickness = thickness
    this._regions = regions ? identify(regions) : {}
    this.conformity = conformity
  }

  public get regions (): Region[] {
    return Object.values(this._regions)
  }

  public get selected (): SelectedType {
    if (this.hasRegions) {
      if (this.regions.every(({ selected }): boolean => !!selected)) {
        return true
      } else if (this.regions.some(({ selected }): boolean => !!selected)) {
        return 'intermediate'
      } else {
        return false
      }
    } else {
      return this._selected
    }
  }

  public set selected (toggled) {
    if (this.hasRegions) {
      this.regions.forEach((region): void => {
        region.selected = toggled
      })
    } else {
      this._selected = toggled
    }
  }

  public get hasRegions (): boolean { return this._regions && this.regions.length > 0 }

  public toJSON (): ZoneSerialization {
    return {
      ...super.toJSON(),
      regions: this.regions.length > 0 ? this.regions.map((region): RegionSerialization => region.toJSON()) : null,
      conformity: this.conformity,
      thickness: this.thickness,
    }
  }
}