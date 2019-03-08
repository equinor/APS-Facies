import uuidv4 from 'uuid/v4'

import { allSet, sortByProperty } from '@/utils'
import { ZoneRegionDependent, Named, BaseItem } from '@/store/utils/domain/bases'

const identify = items => {
  const obj = {}
  items.forEach(item => {
    const _id = item.id || uuidv4()
    obj[`${_id}`] = {
      id: _id,
      ...item,
    }
  })
  return obj
}

const structurePolygons = (polygons, _isParsed = false) => {
  if (_isParsed) return polygons
  return identify(polygons.map((polygon, index) => {
    return {
      ...polygon,
      order: index,
    }
  }))
}

class TruncationRule extends ZoneRegionDependent(Named(BaseItem)) {
  constructor ({ polygons, _polygons, fields, _fields, _realization, ...rest }) {
    super(rest)
    polygons = structurePolygons(polygons, rest._isParsed)

    this.type = null
    this._polygons = polygons || _polygons
    this._fields = fields || _fields

    this._realization = _realization
  }

  specification (context) {}

  get ready () {
    // * Alle facies MÅ være brukt
    // * Overlay MÅ være forskjellig fra bakgrunnsfacies
    // * Grupper (bakgrunnsfacies) kan IKKE være overlappende
    // * I en gruppe;
    //    * En eller flere polygoner
    // * Et GRF kan brukes FLERE ganger i forskjellige grupper
    return allSet(this.fields, 'field') &&
           allSet(this.polygons, 'facies')
  }

  isBackgroundField (field) {
    const id = field.id || field
    const match = this.fields.find(({ field }) => field === id)
    return !match.overlay
  }

  fieldByChannel (channel) {
    return this._fields.find(item => item.channel === channel)
  }

  get polygons () {
    // TODO: Consider using sortByProperty
    return Object.values(this._polygons)
      .sort((a, b) => a.order - b.order)
  }

  get fields () { return this._fields.map(item => { return { ...item, overlay: false } }) }

  get backgroundFields () {
    return this.fields.filter(({ overlay }) => !overlay)
  }

  get minimumRequiredFields () {
    return new Set(this.fields.map(({ field }) => field.name)).size
  }

  get useOverlay () { return false }

  get backgroundPolygons () {
    return this.polygons
      .filter(({ overlay }) => !overlay)
  }
}

const combinePolygons = (polygons, overlay, _isParsed = false) => {
  const combination = []
  const add = (item, overlay = false) => {
    combination.push({ ...item, overlay })
  }
  if (_isParsed) {
    return polygons
  } else {
    if (overlay && overlay.items) overlay = overlay.items
    Object.values(polygons).forEach(polygon => add(polygon, false))
    if (overlay) {
      sortByProperty('order')(overlay).forEach(polygon => add(polygon, true))
    }
    return combination
  }
}

class OverlayedTruncationRule extends TruncationRule {
  constructor ({ polygons, overlay, _useOverlay, ...rest }) {
    super({ polygons: combinePolygons(polygons, overlay, rest._isParsed), ...rest })
    this._useOverlay = typeof _useOverlay === 'undefined'
      ? (overlay ? overlay.use : false)
      : _useOverlay
  }

  fieldByChannel (channel) {
    let field = super.fieldByChannel(channel)
    if (!field) {
      field = this.overlayPolygons.find(polygon => channel === polygon.order + 1 + super.fields.map(({ channel }) => channel).reduce((max, channel) => channel > max ? channel : max, 0))
    }
    return field
  }

  get minimumRequiredFields () {
    const uniqueFields = new Set()
    this.overlayPolygons.forEach(item => {
      item.polygons.forEach(polygon => {
        uniqueFields.add(polygon.field.name)
      })
    })
    return super.minimumRequiredFields + uniqueFields.size
  }

  get useOverlay () { return this._useOverlay }

  get overlayPolygons () {
    return this.useOverlay
      ? this.polygons
        .filter(({ overlay }) => !!overlay)
      : []
  }

  get fields () {
    const fields = super.fields.slice()
    const overlay = this.overlayPolygons
    if (overlay) {
      const channel = fields.map(({ channel }) => channel).reduce((max, channel) => channel > max ? channel : max, 0) + 1
      Object.values(overlay).forEach(polygon => {
        fields.push({
          channel: channel + polygon.order,
          field: polygon.field || '',
          overlay: true,
        })
      })
    }
    return fields
  }

  specification ({ rootGetters }) {
    const getFieldName = (id) => {
      return rootGetters.fields.find(field => field.id === id).name
    }
    return {
      overlay: this.overlayPolygons.length > 0
        ? this.overlayPolygons.map(polygon => {
          return {
            over: rootGetters['facies/name'](polygon.group),
            facies: rootGetters['facies/name'](polygon.facies),
            field: getFieldName(polygon.field),
            center: polygon.center,
            fraction: polygon.fraction,
            order: polygon.order,
          }
        })
        : null
    }
  }
}

class Bayfill extends TruncationRule {
  constructor ({ ...rest }) {
    super(rest)
    this.type = 'bayfill'
  }

  get faciesNames () { return this.polygons.map(facies => facies.name) }

  get values () {
    return {}
  }

  specification (context) {
    const _mapping = {
      'Floodplain': 'SF',
      'Subbay': 'YSF',
      'Bayhead Delta': 'SBHD',
    }
    return this.polygons
      .filter(polygon => !!polygon.factor)
      .map(polygon => { return { ...polygon, name: _mapping[polygon.name] } })
  }
}

class NonCubic extends OverlayedTruncationRule {
  constructor ({ ...rest }) {
    super(rest)
    this.type = 'non-cubic'
  }

  specification ({ rootGetters }) {
    return {
      ...super.specification({ rootGetters }),
      polygons: this.backgroundPolygons
        .map(polygon => {
          const name = rootGetters['facies/name'](polygon.facies)
          return {
            order: polygon.order,
            facies: name,
            angle: polygon.angle,
            fraction: polygon.fraction,
            updatable: polygon.updatable,
          }
        })
    }
  }
}

export {
  TruncationRule,
  Bayfill,
  NonCubic,
}
