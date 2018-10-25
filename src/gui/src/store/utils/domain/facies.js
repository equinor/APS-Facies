import { SelectableItem } from '@/store/utils/domain/bases'

export class Facies extends SelectableItem {
  constructor ({ code, name, alias, color, selected, _id, probabilityCube = null, previewProbability = null }) {
    super({ code, name, selected, _id })
    this.color = color
    this.alias = alias || name
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }
}
