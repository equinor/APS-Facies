import { SelectableItem } from '@/store/utils/domain/bases'

export class Region extends SelectableItem {
  constructor ({ code, name, _id, selected }) {
    super({ code, name, _id, selected })
  }
}
