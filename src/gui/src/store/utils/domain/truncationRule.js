import uuidv4 from 'uuid/v4'
import { cloneDeep } from 'lodash'

import { allSet } from '@/utils'
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
      order: index,
      ...polygon,
    }
  }))
}

const structureSettings = (settings, polygons, _isParsed = false) => {
  if (_isParsed) return settings
  const structured = {}
  Object.values(polygons)
    .forEach(polygon => {
      let setting = settings.find(setting => setting.polygon === polygon.name)
      if (!setting) {
        // TODO: Add settings from overlay / remove from polygon
        setting = cloneDeep(polygon)
      }
      structured[polygon.id] = setting
    })
  return structured
}

class TruncationRule extends ZoneRegionDependent(Named(BaseItem)) {
  constructor ({ polygons, fields, _fields, settings, _realization, ...rest }) {
    super(rest)
    polygons = structurePolygons(polygons, rest._isParsed)
    settings = structureSettings(settings, polygons, rest._isParsed)

    this.type = null
    this.polygons = polygons
    this._fields = fields || _fields
    this.settings = settings

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

  get fields () { return this._fields.map(item => { return { ...item, overlay: false } }) }

  get backgroundFields () {
    return this.backgroundPolygons
      .map(polygon => this.fields.find(field => field.id === polygon.field))
  }

  get minimumRequiredFields () {
    return new Set(this.fields.map(({ field }) => field.name)).size
  }

  get useOverlay () { return false }

  get backgroundPolygons () {
    return Object.values(this.polygons)
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
      Object.values(overlay).forEach(polygon => add(polygon, true))
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
      ? Object.values(this.polygons)
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
            over: polygon.group.map(faciesId => rootGetters['facies/name'](faciesId)),
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
    return Object.values(this.settings)
      .filter(setting => !!setting.factor)
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
          const settings = this.settings[`${polygon.id}`]
          const name = rootGetters['facies/name'](polygon.facies)
          return {
            order: polygon.order,
            facies: name,
            angle: settings.angle,
            fraction: settings.fraction,
            updatable: settings.updatable,
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
