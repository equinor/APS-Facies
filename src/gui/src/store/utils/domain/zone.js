import { Selectable, CodeName, BaseItem } from '@/store/utils/domain/bases'

export class Zone extends Selectable(CodeName(BaseItem)) {
  constructor ({ ...rest }) {
    super(rest)
    this.regions = {}
  }
}
