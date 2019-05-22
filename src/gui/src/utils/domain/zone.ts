import { Identified } from '@/utils/domain/types'
import SelectableItem, { SelectableItemConfiguration, SelectableSerialization } from './bases/selectableItem'
import Region, { RegionSerialization } from './region'

type Regions = Identified<Region>

export interface ZoneSerialization extends SelectableSerialization {
  regions: RegionSerialization[] | null
}

export default class Zone extends SelectableItem {
  public regions: Regions
  public constructor (config: SelectableItemConfiguration) {
    super(config)
    this.regions = {}
  }

  public toJSON (): ZoneSerialization {
    return {
      ...super.toJSON(),
      regions: Object.values(this.regions)
    }
  }
}
