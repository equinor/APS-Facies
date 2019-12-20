import { RootGetters, RootState, Store } from '@/store/typing'
import { hasParents } from '@/utils'
import { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import TruncationRuleBase from '@/utils/domain/truncationRule/base'
import {
  Bayfill,
  Cubic,
  CubicPolygon,
  GaussianRandomField,
  NonCubic,
  OverlayPolygon,
  Parent,
  Polygon,
} from '@/utils/domain'
import Variogram from '@/utils/domain/gaussianRandomField/variogram'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import { Identified } from '@/utils/domain/bases/interfaces'
import { getFaciesName } from '@/utils/queries'

class APSExportError extends Error {
  public constructor (message: string) {
    super(message)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APSExportError)
    }
    this.name = 'APSExportError'
  }
}

interface Context {
  rootState: RootState
  rootGetters: RootGetters
}

type Value = string | number

/**
 * Generic method to create an xml element from input. This method does not handle connecting the element to
 * any parent, nor does it add any child elements.
 * @param doc A document instance created using document.implementation.createDocument
 * @param elemName name of the element (tag) to be created
 * @param elemValue null | the value between start and end-tags (not child elements)
 * @param attributes: null | an array of objects in the form  {name: '<name>', value: '<value>'}
 * @returns {HTMLElement | any | ActiveX.IXMLDOMElement}
 */
function createElement (doc: Document, elemName: string, elemValue?: Value | null, attributes?: null | { name: string, value: Value }[]): HTMLElement {
  const elem = doc.createElement(elemName)
  if (attributes) {
    attributes.forEach((attribute): void => {
      elem.setAttribute(attribute.name, String(attribute.value))
    })
  }
  if (elemValue || elemValue === 0) {
    elem.append(document.createTextNode(String(elemValue)))
  }
  return elem
}

function addRMSProjectName ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const name = rootState.parameters.names.project.selected || '[ UNKNOWN ]'
  parentElement.appendChild(createElement(doc, 'RMSProjectName', name))
}

function addRMSWorkflowName ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = rootState.parameters.names.workflow.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'RMSWorkflowName', value))
  }
}

function addGridModelName ({ rootGetters }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = rootGetters.gridModel
  if (value) {
    parentElement.appendChild(createElement(doc, 'GridModelName', value))
  } else {
    throw new APSExportError('No grid model is selected')
  }
}

function addZoneParamName ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
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

function addRegionParamName ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  if (rootState.regions.use) {
    parentElement.appendChild(createElement(doc, 'RegionParamName', rootState.parameters.region.selected))
  }
}

function addResultFaciesParamName ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = rootState.parameters.realization.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'ResultFaciesParamName', value))
  } else {
    throw new APSExportError('No result facies parameter is given')
  }
}

function addPrintInfo ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = 'DummyValue: What goes here?'
  if (value) {
    parentElement.appendChild(createElement(doc, 'PrintInfo', rootState.parameters.debugLevel.selected))
  }
}

function addSeedFile ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = 'DummyValue: What goes here??? Seed.dat is said to be default value?'
  if (value) {
    // hard coded to seed.dat
    parentElement.appendChild(createElement(doc, 'SeedFile', 'seed.dat'))
  }
}

function addWriteSeeds ({ rootState }: Context, doc: Document, parentElement: HTMLElement): void {
  const value = 'No'
  if (value) {
    parentElement.appendChild(createElement(doc, 'WriteSeeds', value))
  }
}

function addMainFaciesTable ({ rootState, rootGetters }: Context, doc: Document, parentElement: HTMLElement): void {
  // getting blockedWell and blockedWellLog
  const bwParam = rootState.parameters.blockedWell
  const bwLogParam = rootState.parameters.blockedWellLog
  const mainFaciesElement = createElement(doc, 'MainFaciesTable', null, [
    { name: 'blockedWell', value: bwParam.selected || '' },
    { name: 'blockedWellLog', value: bwLogParam.selected || '' },
  ])
  parentElement.appendChild(mainFaciesElement)
  // finding all available facies
  const allFacies = rootGetters['faciesTable']
  allFacies.forEach((facies): void => {
    const faciesElem = createElement(doc, 'Facies', null, [{ name: 'name', value: facies.name }])
    mainFaciesElement.append(faciesElem)
    const codeElem = createElement(doc, 'Code', facies.code)
    faciesElem.append(codeElem)
  })
}

function addFaciesProb ({ rootState, rootGetters }: Context, doc: Document, parent: Parent, zoneElement: HTMLElement): void {
  const probModelElem = createElement(doc, 'FaciesProbForModel')
  zoneElement.append(probModelElem)

  const relevantFacies = Object.values(rootState.facies.available)
    .filter((facies): boolean => hasParents(facies, parent.zone, parent.region))
  if (relevantFacies.length === 0) {
    let message = ''
    if (parent.region) {
      message = `Zone ${parent.zone.code} / region ${parent.region.code}`
    } else {
      message = `Zone ${parent.zone.code}`
    }
    throw new APSExportError(message + ' has no selected facies')
  }

  relevantFacies.forEach((facies): void => {
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
    if (!value && value !== 0) {
      let errMessage = `No ${valueSource} given for facies ${faciesName} in Zone ${parent.zone.code}`
      if (parent.region) {
        errMessage = errMessage + ` Region ${parent.region.code}`
      }
      throw new APSExportError(errMessage)
    }
    probFaciesElem.append(createElement(doc, 'ProbCube', value))
  })
}

function addVariogram (doc: Document, variogram: Variogram, baseKw: string, fieldElement: HTMLElement): void {
  const variogramElement = createElement(doc, 'Vario', null, [{ name: 'name', value: variogram.type }])

  variogramElement.append(createElement(doc, 'MainRange',
    variogram.range.main.value,
    variogram.range.main.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_MAINRANGE' }] : null))

  variogramElement.append(createElement(doc, 'PerpRange',
    variogram.range.perpendicular.value,
    variogram.range.perpendicular.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_PERPRANGE' }] : null))

  variogramElement.append(createElement(doc, 'VertRange',
    variogram.range.vertical.value,
    variogram.range.vertical.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_VERTRANGE' }] : null))

  variogramElement.append(createElement(doc, 'AzimuthAngle',
    variogram.angle.azimuth.value,
    variogram.angle.azimuth.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_AZIMUTHANGLE' }] : null))

  variogramElement.append(createElement(doc, 'DipAngle',
    variogram.angle.dip.value,
    variogram.angle.dip.updatable ? [{ name: 'kw', value: baseKw + '_RESIDUAL_DIPANGLE' }] : null))

  if (variogram.type === 'GENERAL_EXPONENTIAL') {
    variogramElement.append(createElement(doc, 'Power',
      variogram.power.value,
      variogram.power.updatable ? [{ name: 'kw', value: baseKw + '_POWER' }] : null))
  }

  fieldElement.append(variogramElement)
}

function addTrend (doc: Document, field: GaussianRandomField, parent: Parent, baseKw: string, fieldElement: HTMLElement): void {
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
      // relativeSize is specific to EllipticCone3D
      trendTypeElement.append(createElement(doc, 'relativeSize', relativeSize.value,
        relativeSize.updatable ? [{ name: 'kw', value: baseKw + '_RELATIVE_SIZE' }] : null))
    }

    if (trendType !== 'Linear3D') {
      // Origin information applies to everything not Linear3D

      // origin, x direction,
      trendTypeElement.append(createElement(doc, 'origin_x', originX.value,
        originX.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_X' }] : null))

      // origin, y direction,
      trendTypeElement.append(createElement(doc, 'origin_y', originY.value,
        originY.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Y' }] : null))

      // origin, z direction (simulation box)
      trendTypeElement.append(createElement(doc, 'origin_z_simbox', originZ.value,
        originZ.updatable ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Z_SIMBOX' }] : null))

      // origin type
      trendTypeElement.append(createElement(doc, 'origintype', originType))
    }
  }
}

function addGaussianRandomField (doc: Document, field: GaussianRandomField, parent: Parent, zoneElement: HTMLElement): void {
  const fieldElement = createElement(doc, 'GaussField', null, [{ name: 'name', value: field.name }])
  zoneElement.append(fieldElement)
  // generating a base string to be used in kw attributes for this field.
  const regionCode = parent.region ? parent.region.code : 0
  const baseKw = `APS_${parent.zone.code}_${regionCode}_GF_${field.name}`
  // attach vario, trend, relative standard deviation and seed to field:
  addVariogram(doc, field.variogram, baseKw, fieldElement)
  if (field.trend.use && field.trend.type !== 'NONE') {
    addTrend(doc, field, parent, baseKw, fieldElement)
    fieldElement.append(createElement(doc, 'RelStdDev',
      field.trend.relativeStdDev.value, field.trend.relativeStdDev.updatable ? [{ name: 'kw', value: baseKw + '_RELSTDDEV' }] : null))
  }
  fieldElement.append(createElement(doc, 'SeedForPreview', field.settings.seed))
}

function addGaussianRandomFields ({ rootState }: Context, doc: Document, parent: Parent, zoneElement: HTMLElement): void {
  const relevantFields = Object.values(rootState.gaussianRandomFields.available)
    .filter((field): boolean => hasParents(field, parent.zone.id, parent.region ? parent.region.id : null))
    .sort((a, b): number => a.name.localeCompare(b.name, undefined, { numeric: true }))
  if (relevantFields.length < 2) {
    let message = ''
    if (parent.region) {
      message = `Zone ${parent.zone.code} / region ${parent.region.code}`
    } else {
      message = `Zone ${parent.zone.code}`
    }
    throw new APSExportError(message + ' has less than 2 Gaussian Random Fields')
  } else {
    relevantFields.forEach((field): void => {
      addGaussianRandomField(doc, field, parent, zoneElement)
    })
  }
}

function getNumberOfFieldsForTruncRule ({ rootState }: Context, parent: Parent): number {
  const relevantFields = Object.values(rootState.gaussianRandomFields.available)
    .filter((field): boolean => hasParents(field, parent.zone.id, parent.region ? parent.region.id : null))
  return relevantFields ? relevantFields.length : 0
}

function findFaciesNameForNamedPolygon (truncRule: Bayfill, polygonName: string): string {
  const polygonInRule = truncRule.polygons.find((polygon): boolean => polygon.name === polygonName)
  return polygonInRule && polygonInRule.facies
    ? polygonInRule.facies.name
    : ''
}

function getAlphaNames<
  P extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
> (truncRule: TruncationRuleBase<P, S>): string {
  const alphaFields = truncRule.backgroundFields
  return alphaFields.map((field): string => field ? field.name : '').join(' ')
}

function addTruncationRuleBayFill (context: Context, doc: Document, parent: Parent, truncRule: Bayfill, truncRuleElem: HTMLElement): void {
  const numberOfFields = getNumberOfFieldsForTruncRule(context, parent)
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

  truncRule.specification.polygons.forEach((setting): void => {
    BackGroundModelElem.append(createElement(doc, setting.name, setting.factor.value,
      setting.factor.updatable ? [{ name: 'kw', value: baseKw + `_${setting.name}` }] : null))
  })
}

function addTruncationRuleOverlay<
  T extends OverlayTruncationRule<P, S, Sp>,
  P extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  Sp extends PolygonSpecification = PolygonSpecification,
> (
  context: Context,
  doc: Document,
  parent: Parent,
  truncRule: T,
  truncRuleElem: HTMLElement,
  elementName: string,
  backgroundPolygonsHandler: (backGroundModelElem: HTMLElement) => void
): void {
  const { rootState } = context
  const numberOfFields = getNumberOfFieldsForTruncRule(context, parent)
  const truncElement = createElement(doc, elementName, null,
    [{ name: 'nGFields', value: numberOfFields }])
  truncRuleElem.append(truncElement)

  const backGroundModelElem = createElement(doc, 'BackGroundModel')
  truncElement.append(backGroundModelElem)

  const alphaNames = getAlphaNames(truncRule)
  backGroundModelElem.append(createElement(doc, 'AlphaFields', alphaNames))
  // The background polygons
  backgroundPolygonsHandler(backGroundModelElem)

  const overlayGroups: Identified<OverlayPolygon[]> = truncRule.overlayPolygons
    .reduce((obj, polygon): Identified<OverlayPolygon[]> => {
      const groupId = polygon.group.id
      if (!obj.hasOwnProperty(groupId)) obj[`${groupId}`] = []
      obj[`${groupId}`].push(polygon)
      return obj
    }, {})
  if (Object.values(overlayGroups).length > 0 && truncRule.useOverlay) {
    const overLayModelElem = createElement(doc, 'OverLayModel')
    truncElement.append(overLayModelElem)

    Object.keys(overlayGroups).forEach((overlayGroup): void => {
      const groupElement = createElement(doc, 'Group')
      overLayModelElem.append(groupElement)

      overlayGroups[`${overlayGroup}`].forEach((polygon): void => {
        const alphaFieldElement = createElement(
          doc,
          'AlphaField',
          null,
          [{
            name: 'name',
            value: polygon.field ? polygon.field.name : ''
          }])
        groupElement.append(alphaFieldElement)

        alphaFieldElement.append(createElement(doc, 'TruncIntervalCenter', polygon.center))

        alphaFieldElement.append(createElement(
          doc,
          'ProbFrac',
          polygon.fraction,
          [{
            name: 'name',
            value: getFaciesName(polygon),
          }]
        ))
      })
      const group = rootState.facies.groups.available[`${overlayGroup}`]
      group.facies
        .forEach(({ name }): void => groupElement.append(
          createElement(doc, 'BackGround', name)
        ))
    })
  }
}

function addTruncationRuleCubic (context: Context, doc: Document, parent: Parent, truncRule: Cubic, truncRuleElem: HTMLElement): void {
  function handleBackgroundPolygons (backGroundModelElem: HTMLElement): void {
    function addFraction (element: HTMLElement, polygon: CubicPolygon): void {
      element.append(createElement(doc, 'ProbFrac', polygon.fraction, [{ name: 'name', value: getFaciesName(polygon) }]))
    }
    function addPolygon (element: HTMLElement, polygon: CubicPolygon): void {
      if (polygon.children.length > 0) {
        const attributes = !polygon.parent
          ? [{ name: 'direction', value: truncRule.direction.specification }]
          : null
        const child = createElement(doc, `L${polygon.atLevel + 1}`, null, attributes)
        element.append(child)
        polygon.children.forEach((polygon): void => {
          addPolygon(child, polygon)
        })
      } else {
        addFraction(element, polygon)
      }
    }

    if (truncRule.root) {
      addPolygon(backGroundModelElem, truncRule.root)
    }
  }
  addTruncationRuleOverlay(
    context,
    doc,
    parent,
    truncRule,
    truncRuleElem,
    'Trunc2D_Cubic',
    handleBackgroundPolygons,
  )
}

function addTruncationRuleNonCubic (context: Context, doc: Document, parent: Parent, truncRule: NonCubic, truncRuleElem: HTMLElement): void {
  function handleBackgroundPolygons (backGroundModelElem: HTMLElement): void {
    backGroundModelElem.append(createElement(doc, 'UseConstTruncParam', 1)) // See issue 101 (https://git.equinor.com/APS/GUI/issues/101)
    truncRule.backgroundPolygons.forEach((polygon): void => {
      // facies Element
      const faciesName = getFaciesName(polygon)
      const faciesElem = createElement(doc, 'Facies', null, [{ name: 'name', value: faciesName }])
      backGroundModelElem.append(faciesElem)
      // angle element
      const kwValue = `APS_${parent.zone.code}_${parent.region ? parent.region.code : 0}_TRUNC_NONCUBIC_POLYNUMBER_${polygon.order}_ANGLE`
      faciesElem.append(createElement(doc, 'Angle', polygon.angle.value, polygon.angle.updatable ? [{ name: 'kw', value: kwValue }] : null))
      // ProbFrac element
      faciesElem.append(createElement(doc, 'ProbFrac', polygon.fraction))
    })
  }
  addTruncationRuleOverlay(context, doc, parent, truncRule, truncRuleElem, 'Trunc2D_Angle', handleBackgroundPolygons)
}

function addTruncationRule (context: Context, doc: Document, parent: Parent, zoneElement: HTMLElement): void {
  const { rootState } = context
  const truncRuleElem = createElement(doc, 'TruncationRule')
  zoneElement.append(truncRuleElem)

  const truncRule = Object.values(rootState.truncationRules.available).find((rule): boolean => hasParents(rule, parent.zone, parent.region))
  if (!truncRule) {
    let errMessage = `No truncation rule specified for zone ${parent.zone.code}`
    if (parent.region) {
      errMessage = errMessage + ` , region ${parent.region.code}`
    }
    throw new APSExportError(errMessage)
  }
  if (truncRule instanceof Bayfill) {
    addTruncationRuleBayFill(context, doc, parent, truncRule, truncRuleElem)
  }
  if (truncRule instanceof NonCubic) {
    addTruncationRuleNonCubic(context, doc, parent, truncRule, truncRuleElem)
  }
  if (truncRule instanceof Cubic) {
    addTruncationRuleCubic(context, doc, parent, truncRule, truncRuleElem)
  }
}

function addZoneModel (context: Context, doc: Document, parent: Parent, zoneModelsElement: HTMLElement): void {
  const { rootGetters } = context
  const zoneRegionAttributes = []
  zoneRegionAttributes.push({ name: 'number', value: parent.zone.code })
  if (parent.region) {
    zoneRegionAttributes.push({ name: 'regionNumber', value: parent.region.code })
  }
  const zoneElement = createElement(doc, 'Zone', null, zoneRegionAttributes)
  zoneModelsElement.append(zoneElement)

  const { zone } = rootGetters['zones/byCode'](parent.zone.code)
  if (zone.conformity) {
    zoneElement.append(createElement(doc, 'GridLayout', zone.conformity))
  }

  const useConstantProbability = rootGetters['facies/constantProbability'](parent) ? 1 : 0
  zoneElement.append(createElement(doc, 'UseConstProb', useConstantProbability))

  zoneElement.append(createElement(doc, 'SimBoxThickness', rootGetters.simulationSettings({ zone }).simulationBox.z))

  addFaciesProb(context, doc, parent, zoneElement)

  addGaussianRandomFields(context, doc, parent, zoneElement)

  addTruncationRule(context, doc, parent, zoneElement)
}

function addZoneModels (context: Context, doc: Document, parentElement: HTMLElement): void {
  const { rootState } = context
  const zoneModelsElem = createElement(doc, 'ZoneModels', null, null)
  parentElement.appendChild(zoneModelsElem)
  const selectedZones = Object.values(rootState.zones.available)
    .filter((zone): boolean => zone.selected === true || zone.selected === 'intermediate')
    .sort((z1, z2): number => z1.code - z2.code)
  if (selectedZones.length === 0) {
    throw new APSExportError('No zones/regions selected')
  }
  selectedZones.forEach((zone): void => {
    const useRegions = rootState.regions.use && !!rootState.parameters.region.selected
    if (!useRegions) {
      addZoneModel(context, doc, { zone: zone, region: null }, zoneModelsElem)
    } else {
      const selectedRegions = Object.values(zone.regions)
        .filter((region): boolean => !!region.selected)
        .sort((r1, r2): number => r1.code - r2.code)
      selectedRegions.forEach((region): void => {
        addZoneModel(context, doc, { zone: zone, region: region }, zoneModelsElem)
      })
    }
  })
}

function addContent (context: Context, doc: Document, rootElem: HTMLElement): void {
  addRMSProjectName(context, doc, rootElem)
  addRMSWorkflowName(context, doc, rootElem)
  addGridModelName(context, doc, rootElem)
  addZoneParamName(context, doc, rootElem)
  addRegionParamName(context, doc, rootElem)
  addResultFaciesParamName(context, doc, rootElem)
  addPrintInfo(context, doc, rootElem)
  addSeedFile(context, doc, rootElem)
  addWriteSeeds(context, doc, rootElem)
  addMainFaciesTable(context, doc, rootElem)
  addZoneModels(context, doc, rootElem)
}

export function createModel (context: Context): string {
  const doc = document.implementation.createDocument('', '', null)
  const rootElem = createElement(doc, 'APSModel', null, [{ name: 'version', value: '1.0' }])
  doc.appendChild(rootElem)

  addContent(context, doc, rootElem)
  const serializer = new XMLSerializer()
  return serializer.serializeToString(doc)
}

export function extractFmuVariables (doc: string): string {
  const fmuParameters: string[] = (doc.match(/kw=["'][\w\d_]+['"]/gu) || [])
    .map(match => match.split('=')[1].replace(/["']/g, ''))
  return fmuParameters.reduce((content, parameter) => `${content}${parameter}\n`, '')
}

export function createFmuVariables (context: Context): string {
  let doc = createModel(context)
  return extractFmuVariables(doc)
}

export function dumpState (store: Store) {
  let model = null
  let globalFmuVariables = null
  let errorMessage = null
  try {
    model = btoa(createModel({ rootState: store.state, rootGetters: store.getters }))
    globalFmuVariables = extractFmuVariables(model)
  } catch ({ message }) {
    errorMessage = message
  }
  return {
    ...store.state,
    model,
    globalFmuVariables,
    errorMessage,
  }
}
