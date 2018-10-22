import { ZoneRegionDependent } from '@/store/utils/domain/bases'

export class Bayfill extends ZoneRegionDependent {
  constructor ({ polygons, fields, settings, _id, zone, region = null }) {
    super({ _id, zone, region })
    this.polygons = polygons
    this.fields = fields
    this.settings = settings
  }

  get faciesNames () { return this.polygons.map(facies => facies.name) }

  get values () {
    return {}
  }
}
