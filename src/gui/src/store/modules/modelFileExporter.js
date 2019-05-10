import { hasParents } from '@/utils'

class APSExportError extends Error {
  constructor (message) {
    super(message)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APSExportError)
    }
    this.name = 'APSExportError'
  }
}

const addRMSProjectName = (rootState, doc, parentElement) => {
  const value = rootState.parameters.names.project.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'RMSProjectName', value))
  } else {
    throw new APSExportError('The field "APS Model" is not filled')
  }
}

const addRMSWorkFlowName = (rootState, doc, parentElement) => {
  const value = rootState.parameters.names.workflow.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'RMSWorkFlowName', value))
  }
}

const addGridModelName = (rootState, doc, parentElement) => {
  const value = rootState.gridModels.current
  if (value) {
    parentElement.appendChild(createElement(doc, 'GridModelName', value))
  } else {
    throw new APSExportError('No grid model is selected')
  }
}

const addZoneParamName = (rootState, doc, parentElement) => {
  /**
   * zoneParamName : Kommentar fra Oddvar:
   * GUI henter info direkte fra gridet. Workflow leser soneparameteren, men jeg har en funksjon som oppretter
   * soneparameteren hvis den ikke finnes, så det vi kan gjøre er at den pr def skal hete Zone eller Zones
   * (skal sjekke hva som RMS bruker som default i jobben som lager denne). Og hvis den ikke finnes , så
   * oppretter vi den bare. Et søyeblikk så skal jeg gi deg navnet på funksjonen som lager soneparameteren.
   *
   * Default er Zone som navn på soneparameteren i jobben i RMS som heter 'Create Grid Index Parameters ' og
   * som kan brukes til å lage soneparameter m.m
   *
   * Den jobben jeg laga ligger under grid_model.py under src/utils/roxar og heter createZoneParameter.
   * Den har pr i dag ikke blitt brukt til noe og jeg må endre default navnet til Zone for den RMS parameteren den lager.
   */
  const value = rootState.parameters.zone.selected || 'Zone'
  if (value) {
    parentElement.appendChild(createElement(doc, 'ZoneParamName', value))
  } else {
    throw new APSExportError('No Zone parameter is selected')
  }
}

const addRegionParamName = (rootState, doc, parentElement) => {
  const value = rootState.parameters.region.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'RegionParamName', value))
  }
}

const addResultFaciesParamName = (rootState, doc, parentElement) => {
  const value = rootState.parameters.realization.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'ResultFaciesParamName', value))
  } else {
    throw new APSExportError('No result facies parameter is given')
  }
}

const addPrintInfo = (rootState, doc, parentElement) => {
  const value = 'DummyValue: What goes here?'
  if (value) {
    // setting to 0:
    parentElement.appendChild(createElement(doc, 'PrintInfo', 0))
  }
}

const addSeedFile = (rootState, doc, parentElement) => {
  const value = 'DummyValue: What goes here??? Seed.dat is said to be default value?'
  if (value) {
    // hard coded to seed.dat
    parentElement.appendChild(createElement(doc, 'SeedFile', 'seed.dat'))
  }
}

const addWriteSeeds = (rootState, doc, parentElement) => {
  const value = 'No'
  if (value) {
    parentElement.appendChild(createElement(doc, 'WriteSeeds', value))
  }
}

const addMainFaciesTable = (rootState, doc, parentElement) => {
  // getting blockedWell and blockedWellLog
  const bwParam = rootState.parameters.blockedWell
  const bwlogParam = rootState.parameters.blockedWellLog
  const mainFaciesElement = createElement(doc, 'MainFaciesTable', null, [{ name: 'blockedWell', value: bwParam.selected }, { name: 'blockedWellLog', value: bwlogParam.selected }])
  parentElement.appendChild(mainFaciesElement)
  // finding all available facies
  const allFacies = Object.values(rootState.facies.global.available)
  allFacies.forEach(facies => {
    const faciesElem = createElement(doc, 'Facies', null, [{ name: 'name', value: facies.name }])
    mainFaciesElement.append(faciesElem)
    const codeElem = createElement(doc, 'Code', facies.code)
    faciesElem.append(codeElem)
  })
}

const addZoneModels = ({ rootState, rootGetters }, doc, parentElement) => {
  const zoneModelsElem = createElement(doc, 'ZoneModels', null, null)
  parentElement.appendChild(zoneModelsElem)
  const selectedZones = Object.values(rootState.zones.available)
    .filter(zone => zone.selected === true || zone.selected === 'intermediate')
    .sort((z1, z2) => z1.code - z2.code)
  if (selectedZones.length === 0) {
    throw new APSExportError('No zones/regions selected')
  }
  selectedZones.forEach(zone => {
    const useRegions = rootState.regions.use && !!rootState.parameters.region.selected
    if (!useRegions) {
      addZoneModel({ rootState, rootGetters }, doc, { zone: zone, region: null }, zoneModelsElem)
    } else {
      const selectedRegions = Object.values(zone.regions)
        .filter(region => !!region.selected)
        .sort((r1, r2) => r1.code - r2.code)
      selectedRegions.forEach(region => {
        addZoneModel({ rootState, rootGetters }, doc, { zone: zone, region: region }, zoneModelsElem)
      })
    }
  })
}

const addZoneModel = ({ rootState, rootGetters }, doc, parent, zoneModelsElement) => {
  const zoneRegionAttributes = []
  zoneRegionAttributes.push({ name: 'number', value: parent.zone.code })
  if (parent.region) {
    zoneRegionAttributes.push({ name: 'regionNumber', value: parent.region.code })
  }
  const zoneElement = createElement(doc, 'Zone', null, zoneRegionAttributes)
  zoneModelsElement.append(zoneElement)

  const useConstantProbability = rootGetters['facies/constantProbability'](parent) ? 1 : 0
  zoneElement.append(createElement(doc, 'UseConstProb', useConstantProbability))

  zoneElement.append(createElement(doc, 'SimBoxThickness', rootGetters.simulationSettings().simulationBox.z))

  addFaciesProb({ rootState, rootGetters }, doc, parent, zoneElement)

  addGaussianRandomFields(rootState, doc, parent, zoneElement)

  addTruncationRule({ rootState }, doc, parent, zoneElement)
}

const addGaussianRandomFields = (rootState, doc, parent, zoneElement) => {
  const relevantFields = Object.values(rootState.gaussianRandomFields.fields)
    .filter(field => hasParents(field, parent.zone.id, parent.region ? parent.region.id : null))
    .sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))
  if (relevantFields.length < 2) {
    let message = ''
    if (parent.region) {
      message = `Zone ${parent.zone.code} / region ${parent.region.code}`
    } else {
      message = `Zone ${parent.zone.code}`
    }
    throw new APSExportError(message + ' has less than 2 Gaussian Random Fields')
  } else {
    relevantFields.forEach(field => {
      addGaussianRandomField(doc, field, parent, zoneElement)
    })
  }
}

const addGaussianRandomField = (doc, field, parent, zoneElement) => {
  const fieldElement = createElement(doc, 'GaussField', null, [{ name: 'name', value: field.name }])
  zoneElement.append(fieldElement)
  // generating a base string to be used in kw attributes for this field.
  const regionCode = parent.region ? parent.region.code : 0
  const baseKw = `APS_${parent.zone.code}_${regionCode}_GF_${field.name}`
  // attach vario, trend, relative standard deviation and seed to field:
  addVario(doc, field.variogram, baseKw, fieldElement)
  if (field.trend.use && field.trend.type !== 'NONE') {
    addTrend(doc, field, parent, baseKw, fieldElement)
    fieldElement.append(createElement(doc, 'RelStdDev',
      field.trend.relativeStdDev.value, field.trend.relativeStdDev.updatable ? [{ name: 'kw', value: baseKw + '_RELSTDDEV' }] : null))
  }
  // TODO / Future: Consider if the value here should be the same as the last used seed in the gui.
  fieldElement.append(createElement(doc, 'SeedForPreview', '0'))
}

const addVario = (doc, variogram, baseKw, fieldElement) => {
  const varioElement = createElement(doc, 'Vario', null, [{ name: 'name', value: variogram.type }])

  varioElement.append(createElement(doc, 'MainRange',
    variogram.range.main.value,
    variogram.range.main.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_MAINRANGE' }] : null))

  varioElement.append(createElement(doc, 'PerpRange',
    variogram.range.perpendicular.value,
    variogram.range.perpendicular.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_PERPRANGE' }] : null))

  varioElement.append(createElement(doc, 'VertRange',
    variogram.range.vertical.value,
    variogram.range.vertical.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_VERTRANGE' }] : null))

  varioElement.append(createElement(doc, 'AzimuthAngle',
    variogram.angle.azimuth.value,
    variogram.angle.azimuth.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_AZIMUTHANGLE' }] : null))

  varioElement.append(createElement(doc, 'DipAngle',
    variogram.angle.dip.value,
    variogram.angle.dip.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_DIPANGLE' }] : null))

  if (variogram.type === 'GENERAL_EXPONENTIAL') {
    varioElement.append(createElement(doc, 'Power',
      variogram.power.value,
      variogram.power.updatable ? [{ name: 'kw', value: baseKw + '_POWER' }] : null))
  }

  fieldElement.append(varioElement)
}

const addTrend = (doc, field, parent, baseKw, fieldElement) => {
  const trendElement = createElement(doc, 'Trend', null, null)
  fieldElement.append(trendElement)

  // mapping from trend type names used in the store to the ones to be used in the exported file.
  const trendTypeMap = new Map()
  trendTypeMap.set('RMS_PARAM', 'RMSParameter')
  trendTypeMap.set('LINEAR', 'Linear3D')
  trendTypeMap.set('ELLIPTIC', 'Elliptic3D')
  trendTypeMap.set('HYPERBOLIC', 'Hyperbolic3D')
  trendTypeMap.set('ELLIPTIC_CONE', 'EllipticCone3D')
  const trendType = trendTypeMap.get(field.trend.type)
  if (!trendType) {
    throw new Error('Unknown trendType')
  }

  // fields in store that might be used depending on trendType
  const rmsTrendParam = field.trend.parameter
  const azimuth = field.trend.angle.azimuth
  const stackingDirection = field.trend.stackingDirection
  const stackAngle = field.trend.angle.stacking
  const migrationAngle = field.trend.angle.migration
  const curvature = field.trend.curvature
  const originX = field.trend.origin.x
  const originY = field.trend.origin.y
  const originZ = field.trend.origin.z
  const originType = field.trend.origin.type
  const relativeSize = field.trend.relativeSize

  // adding the element directly under the trendElement, containing the type of Trend
  const trendTypeElement = createElement(doc, trendType, null, null)
  trendElement.append(trendTypeElement)

  // adding the parameters specific to each trend type
  if (trendType === 'RMSParameter') {
    const trendParamName = createElement(doc, 'TrendParamName', rmsTrendParam, null)
    trendTypeElement.append(trendParamName)
  } else {
    // azimuth, directionStacking and stackAngle common to all trends except rms parameter

    // azimuth
    trendTypeElement.append(createElement(doc, 'azimuth',
      azimuth.value, azimuth.updatable ? [{ name: 'kw', value: baseKw + '_TREND_AZIMUTH' }] : null))

    // directionStacking
    if (!stackingDirection) {
      if (parent.region) {
        throw new APSExportError(`Missing Stacking direction for field ${field.name} in zone ${parent.zone.code}, region ${parent.region.code}`)
      } else {
        throw new APSExportError(`Missing Stacking direction for field ${field.name} in zone ${parent.zone.code}`)
      }
    }
    trendTypeElement.append(createElement(doc, 'directionStacking', stackingDirection === 'PROGRADING' ? 1 : -1, null))

    // stackAngle
    trendTypeElement.append(createElement(doc, 'stackAngle', stackAngle.value,
      stackAngle.updatable ? [{ name: 'kw', value: baseKw + '_TREND_STACKANGLE' }] : null))

    if (trendType === 'EllipticCone3D' || trendType === 'Hyperbolic3D') {
      // migrationAngle is specific to EllipticCone3D and Hyperbolic3D
      trendTypeElement.append(createElement(doc, 'migrationAngle', migrationAngle.value,
        migrationAngle.updatable ? [{ name: 'kw', value: baseKw + '_TREND_MIGRATIONANGLE' }] : null))
    }

    if (trendType !== 'Linear3D') {
      // curvature is a child of everything not Linear3D (and RMSParameter of course)
      trendTypeElement.append(createElement(doc, 'curvature', curvature.value,
        curvature.updatable ? [{ name: 'kw', value: baseKw + '_TREND_CURVATURE' }] : null))
    }

    if (trendType === 'EllipticCone3D') {
      // relativeSize is spesific to EllipticCone3D
      trendTypeElement.append(createElement(doc, 'curvature', relativeSize.value,
        relativeSize.updatable ? [{ name: 'kw', value: baseKw + 'RELATIVE_SIZE' }] : null))
    }

    if (trendType !== 'Linear3D') {
      // Origin information applies to everything not Linear3D

      // origin_x,
      trendTypeElement.append(createElement(doc, 'origin_x', originX.value,
        originX.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_X' }] : null))

      // origin_y,
      trendTypeElement.append(createElement(doc, 'origin_y', originY.value,
        originY.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Y' }] : null))

      // origin_z_simbox
      trendTypeElement.append(createElement(doc, 'origin_z_simbox', originZ.value,
        originZ.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Z_SIMBOX' }] : null))

      // origintype
      trendTypeElement.append(createElement(doc, 'origintype', originType))
    }
  }
}

const addFaciesProb = ({ rootState, rootGetters }, doc, parent, zoneElement) => {
  const probModelElem = createElement(doc, 'FaciesProbForModel')
  zoneElement.append(probModelElem)

  const relevantFacies = Object.values(rootState.facies.available).filter(
    facies => hasParents(facies, parent.zone, parent.region))
  if (relevantFacies.length === 0) {
    let message = ''
    if (parent.region) {
      message = `Zone ${parent.zone.code} / region ${parent.region.code}`
    } else {
      message = `Zone ${parent.zone.code}`
    }
    throw new APSExportError(message + ' has no selected facies')
  }

  relevantFacies.forEach(facies => {
    // get the facies name from the referenced global facies
    const faciesName = rootGetters['facies/name'](facies)
    const probFaciesElem = createElement(doc, 'Facies', null, [{ name: 'name', value: faciesName }])
    probModelElem.append(probFaciesElem)

    const useConstantProb = rootGetters['facies/constantProbability'](parent)
    let value
    let valueSource

    if (useConstantProb) {
      value = facies.previewProbability
      valueSource = 'probability'
    } else {
      value = facies.probabilityCube
      valueSource = 'probability cube'
    }
    if (!value) {
      let errMessage = `No ${valueSource} given for facies ${faciesName} in Zone ${parent.zone.code}`
      if (parent.region) {
        errMessage = errMessage + ` Region ${parent.region.code}`
      }
      throw new APSExportError(errMessage)
    }
    probFaciesElem.append(createElement(doc, 'ProbCube', value))
  })
}

const addTruncationRule = ({ rootState }, doc, parent, zoneElement) => {
  const truncRuleElem = createElement(doc, 'TruncationRule')
  zoneElement.append(truncRuleElem)

  const truncRule = Object.values(rootState.truncationRules.rules).find(rule => hasParents(rule, parent.zone, parent.region))
  if (!truncRule) {
    let errMessage = `No truncation rule specified for zone ${parent.zone.code}`
    if (parent.region) {
      errMessage = errMessage + ` , region ${parent.region.code}`
    }
    throw new APSExportError(errMessage)
  }
  if (truncRule.type === 'bayfill') {
    addTruncationRuleBayFill({ rootState }, doc, parent, truncRule, truncRuleElem)
  }
  if (truncRule.type === 'non-cubic') {
    addTruncationRuleNonCubic({ rootState }, doc, parent, truncRule, truncRuleElem)
  }
  if (truncRule.type === 'cubic') {
    addTruncationRuleCubic({ rootState }, doc, parent, truncRule, truncRuleElem)
  }
}

const addTruncationRuleBayFill = ({ rootState }, doc, parent, truncRule, truncRuleElem) => {
  const numberOfFields = getNumberOfFieldsForTruncRule({ rootState }, parent)
  const bayFillElem = createElement(doc, 'Trunc3D_Bayfill', null,
    [{ name: 'nGFields', value: numberOfFields }])
  truncRuleElem.append(bayFillElem)

  const BackGroundModelElem = createElement(doc, 'BackGroundModel')
  bayFillElem.append(BackGroundModelElem)

  const alphaNames = getAlphaNames(truncRule)
  BackGroundModelElem.append(createElement(doc, 'AlphaFields', alphaNames))

  BackGroundModelElem.append(createElement(doc, 'UseConstTruncParam', 1)) // See issue 101 (https://git.equinor.com/APS/GUI/issues/101)

  // polygons
  BackGroundModelElem.append(createElement(doc, 'Floodplain',
    findFaciesNameForNamedPolygon(truncRule, 'Floodplain')))
  BackGroundModelElem.append(createElement(doc, 'Subbay',
    findFaciesNameForNamedPolygon(truncRule, 'Subbay')))
  BackGroundModelElem.append(createElement(doc, 'WBF',
    findFaciesNameForNamedPolygon(truncRule, 'Wave influenced Bayfill')))
  BackGroundModelElem.append(createElement(doc, 'BHD',
    findFaciesNameForNamedPolygon(truncRule, 'Bayhead Delta')))
  BackGroundModelElem.append(createElement(doc, 'Lagoon',
    findFaciesNameForNamedPolygon(truncRule, 'Lagoon')))

  // slant factors
  const baseKw = `APS_${parent.zone.code}_${parent.region ? parent.region.code : 0}_TRUNC_BAYFILL`

  truncRule.specification.forEach(setting => {
    BackGroundModelElem.append(createElement(doc, setting.name, setting.factor.value,
      setting.factor.updatable ? [{ name: 'kw', value: baseKw + `_${setting.name}` }] : null))
  })
}

const addTruncationRuleOverlay = ({ rootState }, doc, parent, truncRule, truncRuleElem, elementName, backgroundPolygonsHandler) => {
  const numberOfFields = getNumberOfFieldsForTruncRule({ rootState }, parent)
  const truncElement = createElement(doc, elementName, null,
    [{ name: 'nGFields', value: numberOfFields }])
  truncRuleElem.append(truncElement)

  const backGroundModelElem = createElement(doc, 'BackGroundModel')
  truncElement.append(backGroundModelElem)

  const alphaNames = getAlphaNames(truncRule)
  backGroundModelElem.append(createElement(doc, 'AlphaFields', alphaNames))
  // The background polygons
  backgroundPolygonsHandler(backGroundModelElem)

  const overlayGroups = truncRule.overlayPolygons
    .reduce((obj, polygon) => {
      const groupId = polygon.group.id
      if (!obj.hasOwnProperty(groupId)) obj[`${groupId}`] = []
      obj[`${groupId}`].push(polygon)
      return obj
    }, {})
  if (Object.values(overlayGroups).length > 0 && truncRule.useOverlay) {
    const overLayModelElem = createElement(doc, 'OverLayModel')
    truncElement.append(overLayModelElem)

    Object.keys(overlayGroups).forEach(overlayGroup => {
      const groupElement = createElement(doc, 'Group')
      overLayModelElem.append(groupElement)

      overlayGroups[`${overlayGroup}`].forEach(polygon => {
        const alphaFieldElement = createElement(
          doc,
          'AlphaField',
          null,
          [{
            name: 'name',
            value: polygon.field.name
          }])
        groupElement.append(alphaFieldElement)

        alphaFieldElement.append(createElement(doc, 'TruncIntervalCenter', polygon.center))

        alphaFieldElement.append(createElement(
          doc,
          'ProbFrac',
          polygon.fraction,
          [{
            name: 'name',
            value: polygon.facies.name
          }]
        ))
      })
      const group = rootState.facies.groups.available[`${overlayGroup}`]
      group.facies
        .forEach(({ name }) => groupElement.append(
          createElement(doc, 'BackGround', name)
        ))
    })
  }
}

const addTruncationRuleNonCubic = ({ rootState }, doc, parent, truncRule, truncRuleElem) => {
  function handleBackgroundPolygons (backGroundModelElem) {
    backGroundModelElem.append(createElement(doc, 'UseConstTruncParam', 1)) // See issue 101 (https://git.equinor.com/APS/GUI/issues/101)
    truncRule.backgroundPolygons.forEach(polygon => {
      // facies Element
      const faciesName = polygon.facies.name
      const faciesElem = createElement(doc, 'Facies', null, [{ name: 'name', value: faciesName }])
      backGroundModelElem.append(faciesElem)
      // angle element
      const kwValue = `APS_${parent.zone.code}_${parent.region ? parent.region.code : 0}_TRUNC_NONCUBIC_POLYNUMBER_${faciesName}_ANGLE`
      faciesElem.append(createElement(doc, 'Angle', polygon.angle.value, polygon.angle.updatable ? [{ name: 'kw', value: kwValue }] : null))
      // ProbFrac element
      faciesElem.append(createElement(doc, 'ProbFrac', polygon.fraction))
    })
  }
  addTruncationRuleOverlay({ rootState }, doc, parent, truncRule, truncRuleElem, 'Trunc2D_Angle', handleBackgroundPolygons)
}

const addTruncationRuleCubic = ({ rootState }, doc, parent, truncRule, truncRuleElem) => {
  function handleBackgroundPolygons (backGroundModelElem) {
    function addFraction (element, polygon) {
      element.append(createElement(doc, 'ProbFrac', polygon.fraction, [{ name: 'name', value: polygon.facies.name }]))
    }
    function addPolygon (element, polygon) {
      if (polygon.facies) {
        addFraction(element, polygon)
      } else {
        const attributes = !polygon.parent
          ? [{ name: 'direction', value: truncRule.direction.specification }]
          : null
        const child = createElement(doc, `L${polygon.atLevel + 1}`, null, attributes)
        element.append(child)
        polygon.children.forEach(polygon => {
          addPolygon(child, polygon)
        })
      }
    }

    addPolygon(backGroundModelElem, truncRule.root)
  }
  addTruncationRuleOverlay(
    { rootState },
    doc,
    parent,
    truncRule,
    truncRuleElem,
    'Trunc2D_Cubic',
    handleBackgroundPolygons,
  )
}

const getNumberOfFieldsForTruncRule = ({ rootState }, parent) => {
  const relevantFields = Object.values(rootState.gaussianRandomFields.fields).filter(
    field => hasParents(field, parent.zone.id, parent.region ? parent.region.id : null))
  return relevantFields ? relevantFields.length : 0
}

const getAlphaNames = (truncRule) => {
  const alphaFields = truncRule.backgroundFields
  return alphaFields.map(field => field.name).join(' ')
}

const findFaciesNameForNamedPolygon = (truncRule, polygonName) => {
  const polygonInRule = truncRule.polygons.find(polygon => polygon.name === polygonName)
  return polygonInRule.facies.facies.name
}

/**
 * Generic method to create an xml element from input. This method does not handle connecting the element to
 * any parent, nor does it add any child elements.
 * @param doc A document instance created using document.implementation.createDocument
 * @param elemName name of the element (tag) to be created
 * @param elemValue null | the value between start and end-tags (not child elements)
 * @param attributes: null | an array of objects in the form  {name: '<name>', value: '<value>'}
 * @returns {HTMLElement | any | ActiveX.IXMLDOMElement}
 */
const createElement = (doc, elemName, elemValue, attributes) => {
  const elem = doc.createElement(elemName)
  if (attributes) {
    attributes.forEach(attribute => {
      elem.setAttribute(attribute.name, attribute.value)
    })
  }
  if (elemValue || elemValue === 0) {
    elem.append(document.createTextNode(elemValue))
  }
  return elem
}

export default {
  namespaced: true,

  actions: {
    createModelFileFromStore: ({ rootState, rootGetters }) => {
      return new Promise((resolve, reject) => {
        const doc = document.implementation.createDocument('', '', null)
        const rootElem = createElement(doc, 'APSModel', null, [{ name: 'version', value: '1.0' }])
        doc.appendChild(rootElem)
        try {
          addRMSProjectName(rootState, doc, rootElem)
          addRMSWorkFlowName(rootState, doc, rootElem)
          addGridModelName(rootState, doc, rootElem)
          addZoneParamName(rootState, doc, rootElem)
          addRegionParamName(rootState, doc, rootElem)
          addResultFaciesParamName(rootState, doc, rootElem)
          addPrintInfo(rootState, doc, rootElem)
          addSeedFile(rootState, doc, rootElem)
          addWriteSeeds(rootState, doc, rootElem)
          addMainFaciesTable(rootState, doc, rootElem)
          addZoneModels({ rootState, rootGetters }, doc, rootElem)
          const serializer = new XMLSerializer()
          const xmlString = serializer.serializeToString(doc)
          resolve(xmlString)
        } catch (error) {
          reject(error)
        }
      })
    }
  }
}
