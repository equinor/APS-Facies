import uuidv4 from 'uuid/v4'

import { ZoneRegionDependent } from '@/store/utils/domain/bases'

const identify = items => {
  const obj = {}
  items.forEach(item => {
    const _id = uuidv4()
    obj[`${_id}`] = {
      id: _id,
      ...item,
    }
  })
  return obj
}

const structurePolygons = (polygons) => {
  return identify(polygons)
}

const structureSettings = (settings, polygons) => {
  const structured = {}
  for (let setting of settings) {
    const polygon = Object.values(polygons).find(polygon => polygon.name === setting.polygon)
    structured[polygon.id] = setting
  }
  return structured
}

class TruncationRule extends ZoneRegionDependent {
  constructor ({ polygons, fields, settings, _id, zone, region = null }) {
    super({ _id, zone, region })
    polygons = structurePolygons(polygons)
    settings = structureSettings(settings, polygons)

    this.type = null
    this.polygons = polygons
    this.fields = fields
    this.settings = settings
  }
}

class Bayfill extends TruncationRule {
  constructor ({ polygons, fields, settings, _id, zone, region = null }) {
    super({ polygons, fields, settings, _id, zone, region })
    this.type = 'bayfill'
  }

  get faciesNames () { return this.polygons.map(facies => facies.name) }

  get values () {
    return {}
  }
}

export {
  Bayfill,
}
