import { Identified } from '@/utils/domain/types'
import SelectableItem, { SelectableItemConfiguration } from './bases/selectableItem'
import Region from './region'

type Regions = Identified<Region>

export default class Zone extends SelectableItem {
  public regions: Regions
  public constructor (config: SelectableItemConfiguration) {
    super(config)
    this.regions = {}
  }
}
