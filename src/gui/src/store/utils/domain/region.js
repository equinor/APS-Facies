import { Selectable, CodeName, BaseItem } from '@/store/utils/domain/bases'

export class Region extends Selectable(CodeName(BaseItem)) {
  constructor ({ ...rest }) {
    super(rest)
  }
}
