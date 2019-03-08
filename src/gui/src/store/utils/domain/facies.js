import { BaseItem, ZoneRegionDependent, CodeName } from '@/store/utils/domain/bases'
import { getId } from '@/utils/typing'

class GlobalFacies extends CodeName(BaseItem) {
  constructor ({ alias, color, ...rest }) {
    super(rest)
    this.color = color
    this.alias = alias || rest.name
  }
}

function checkFaciesId (facies) {
  facies = getId(facies)
  if (!facies) throw new Error(`'facies' MUST be a valid ID (uuid). Was ${facies}`)
  return facies
}

class Facies extends ZoneRegionDependent(BaseItem) {
  constructor ({ facies, probabilityCube = null, previewProbability = null, ...rest }) {
    super(rest)
    facies = checkFaciesId(facies)
    this.facies = facies
    this.probabilityCube = probabilityCube
    this.previewProbability = previewProbability
  }
}

class FaciesGroup extends ZoneRegionDependent(BaseItem) {
  constructor ({ facies, _facies, ...rest }) {
    super(rest)
    facies = facies || _facies
    facies.forEach(facies => {
      checkFaciesId(facies)
    })
    this._facies = facies.map(getId)
  }

  get facies () { return this._facies }

  get length () { return this.facies.length }

  has (facies) {
    return new Set(this.facies).has(getId(facies))
  }

  contains (facies) {
    facies = new Set(facies)
    return this.facies.filter(x => !facies.has(x)).length === 0
  }
}

export {
  GlobalFacies,
  Facies,
  FaciesGroup,
}
