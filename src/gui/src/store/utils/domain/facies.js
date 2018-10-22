import { SelectableItem } from '@/store/utils/domain/bases'

export class Facies extends SelectableItem {
  constructor ({ code, name, color, selected, _id, probabilityCube = null, previewProbability = null }) {
    super({ code, name, selected, _id })
    this.color = color
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }
}
