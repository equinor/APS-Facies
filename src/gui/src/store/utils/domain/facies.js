import { BaseItem, ZoneRegionDependent, CodeName } from '@/store/utils/domain/bases'
import { getId } from '@/utils/typing'

class GlobalFacies extends CodeName(BaseItem) {
  constructor ({ alias, color, ...rest }) {
    super(rest)
    this.color = color
    this.alias = alias || rest.name
  }
}

class Facies extends ZoneRegionDependent(BaseItem) {
  constructor ({ facies, probabilityCube = null, previewProbability = null, ...rest }) {
    super(rest)
    facies = getId(facies)
    if (!facies) throw new Error(`'facies' MUST be a valid ID (uuid). Was ${facies}`)
    this.facies = facies
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }
}

export {
  GlobalFacies,
  Facies,
}
