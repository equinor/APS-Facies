import { SelectableItem } from '@/store/utils/domain/bases'

export class Zone extends SelectableItem {
  constructor ({ code, name, selected }) {
    super({ code, name, selected })
    this.regions = {}
  }
}
