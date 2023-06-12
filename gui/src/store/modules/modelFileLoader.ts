import { RootState, Context as BaseContext } from '@/store/typing'
import { Newable } from '@/utils/domain/bases/interfaces'
import APSError from '@/utils/domain/errors/base'
import FaciesGroup from '@/utils/domain/facies/group'
import GaussianRandomField, { Variogram, Trend } from '@/utils/domain/gaussianRandomField'
import {
  Bayfill,
  BayfillPolygon,
  NonCubic,
  NonCubicPolygon,
  Cubic,
  CubicPolygon,
  OverlayPolygon,
  Facies,
  Polygon,
  Parent,
} from '@/utils/domain'
import { displayMessage } from '@/store/utils'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import { TrendConfiguration, TrendType } from '@/utils/domain/gaussianRandomField/trend'
import { VariogramConfiguration } from '@/utils/domain/gaussianRandomField/variogram'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import { hasOwnProperty } from '@/utils/helpers'
import { Optional } from '@/utils/typing'
import { Module } from 'vuex'

interface XMLElement {
  elements: XMLElement[]
  declaration: any
  [_: string]: any
}

interface JobSettingsParam {
  runFmuWorkflows: boolean
  onlyUpdateFromFmu: boolean
  simulationGrid: string
  importFields: boolean
  fieldFileFormat: string
  customTrendExtrapolationMethod: string
  exportFmuConfigFiles: boolean
  onlyUpdateResidualFields: boolean
  useNonStandardFmu: boolean
  exportErtBoxGrid: boolean
  maxAllowedFractionOfValuesOutsideTolerance: number
  toleranceOfProbabilityNormalisation: number
  transformType: number
  debugLevel: number
}


type Context = BaseContext<Record<string, unknown>, Record<string, unknown>>

class KeywordError extends APSError {
  public constructor (keyword: string) {
    super(`The keyword, '${keyword}' is missing`)
  }
}

function ensureArray<T> (value: T | T[]): T[] {
  return Array.isArray(value)
    ? value
    : [value]
}

function getNodeValue (container: XMLElement, prop: Optional<string> = null): Optional<XMLElement> {
  let value: XMLElement | undefined = container
  if (prop) value = container.elements.find((el): boolean => el.name === prop)
  if (typeof value === 'undefined') return null
  return value
}

function getMandatoryNodeValue (container: XMLElement, prop: string): XMLElement {
  const value = getNodeValue(container, prop)
  if (!value) throw new KeywordError(prop)
  return value
}

function getNodeValues (container: XMLElement, prop: string): XMLElement[] {
  return container.elements
    .filter((el): boolean => el.name === prop)
}

function getName (container: XMLElement, prop: Optional<string> = null): string {
  let value: XMLElement | undefined = container
  if (prop) value = container.elements.find((el): boolean => el.name === prop)
  if (!value) return ''
  return value.attributes.name.trim()
}

function getTextValue (elem: XMLElement, prop: Optional<string> = null): Optional<string> {
  let value = getNodeValue(elem, prop)
  if (!value) return null

  if (value.elements.length === 1 && value.elements[0].type === 'text') {
    value = value.elements[0].text
  }
  if (value) {
    return value.trim()
  }
  return null
}

function getOriginType (elem: XMLElement, prop: Optional<string> = null): 'RELATIVE' | 'ABSOLUTE' {
  let value = getTextValue(elem, prop)
  if (value) {
    value = value.replace(/'/g, '').toUpperCase()
    if (!['RELATIVE', 'ABSOLUTE'].includes(value)) throw new APSError(`The origin typ MUST be one of "RELATIVE", or "ABSOLUTE", but was ${value}`)
  }
  return (value as 'RELATIVE' | 'ABSOLUTE')
}

function isFMUUpdatable (elem: XMLElement, prop: Optional<string> = null): boolean {
  let value = null
  if (prop) value = elem.elements.find((el): boolean => el.name === prop)
  return !!(value && value.attributes && value.attributes.kw)
}

function getNumericValue (elem: XMLElement, prop: Optional<string> = null): Optional<number> {
  const text = getTextValue(elem, prop)
  if (text) {
    return Number(text)
  }
  return null
}

function getMandatoryNumericValue (elem: XMLElement, prop: string): number {
  const value = getNumericValue(elem, prop)
  if (value === null) throw new KeywordError((prop))
  return value
}

function getBooleanValue (elem: XMLElement, prop: Optional<string> = null): Optional<boolean> {
  const value = getNumericValue(elem, prop)
  if (value || value === 0) {
    return Boolean(value)
  }
  return null
}

function getStackingDirection (elem: XMLElement, prop: Optional<string> = null): 'PROGRADING' | 'RETROGRADING' {
  const direction = getTextValue(elem, prop)
  if (direction === '1') { return 'PROGRADING' }
  if (direction === '-1') { return 'RETROGRADING' }
  throw new APSError('Stacking direction is defined incorrectly for trend')
}

function getParent ({ rootGetters }: Context, zoneModel: XMLElement): Parent {
  const zoneNumber = parseInt(zoneModel.attributes.number)
  const regionNumber = zoneModel.attributes.regionNumber
    ? parseInt(zoneModel.attributes.regionNumber)
    : null
  return rootGetters['zones/byCode'](zoneNumber, regionNumber)
}

function getFacies ({ rootState }: Context, name: string, parent: Parent): Facies | undefined {
  return Object.values(rootState.facies.available)
    .filter((facies): boolean => facies.isChildOf(parent))
    .find((facies): boolean => facies.name === name)
}

function getBackgroundFacies (context: Context, container: XMLElement, parent: Parent): Facies[] {
  const over = getNodeValues(container, 'BackGround')

  const backgroundFacies: Facies[] = []
  for (const el of over) {
    const name = getTextValue(el)
    if (name === null) throw new APSError('A Facies had no name')
    const facies = getFacies(context, name, parent)
    if (facies) backgroundFacies.push(facies)
  }
  return backgroundFacies
}

function getFaciesFromBayfill (context: Context, container: XMLElement, item: string, parent: Parent): Facies {
  const mappig = {
    'Bayhead Delta': 'BHD',
    'Wave influenced Bayfill': 'WBF',
  }
  if (item in mappig) item = mappig[`${item}`]
  const backgroundModel = getNodeValue(container, 'BackGroundModel')
  if (!backgroundModel) throw new KeywordError('BackGroundModel')

  const name = getTextValue(backgroundModel, item)
  if (!name) throw new APSError('The polygon does not have a Facies')

  const facies = getFacies(context, name, parent)
  if (!facies) throw new APSError('The Facies has not been added to the internal state')

  return facies
}

function getSlantFactor (container: XMLElement, item: string): Optional<FmuUpdatableValue> {
  const mapping = {
    Floodplain: 'SF',
    Subbay: 'YSF',
    'Bayhead Delta': 'SBHD',
  }
  const element = getNodeValue(container, 'BackGroundModel')
  if (!element) throw new APSError()
  return item in mapping
    ? new FmuUpdatableValue({
      value: getMandatoryNumericValue(element, mapping[`${item}`]),
      updatable: isFMUUpdatable(element, mapping[`${item}`]),
    })
    : null
}

function getAlphaField ({ rootState }: Context, name: string, parent: Parent): GaussianRandomField {
  const field = Object.values(rootState.gaussianRandomFields.available)
    .filter((field): boolean => field.isChildOf(parent))
    .find((field): boolean => field.name === name)
  if (!field) throw new APSError(`The Gaussian Random Field, with name ${name}, and parent; ${parent} does not exist`)
  return field
}

function getAlphaFields (context: Context, container: XMLElement, parent: Parent): GaussianRandomField[] {
  const alphaFields = getTextValue(getMandatoryNodeValue(container, 'BackGroundModel'), 'AlphaFields')
  if (alphaFields === null) throw new KeywordError('AlphaFields')
  return alphaFields.split(' ').map((name: string): GaussianRandomField => getAlphaField(context, name, parent))
}

function getDirection (container: XMLElement): 'V' | 'H' {
  return getMandatoryNodeValue(getMandatoryNodeValue(container, 'BackGroundModel'), 'L1').attributes.direction
}

function makeBayfillTruncationRule (context: Context, container: XMLElement, parent: Parent): Bayfill {
  const names = [
    'Floodplain',
    'Subbay',
    'Wave influenced Bayfill',
    'Bayhead Delta',
    'Lagoon',
  ]
  const polygons = names.map((name, index): BayfillPolygon => {
    return new BayfillPolygon({
      name,
      facies: getFaciesFromBayfill(context, container, name, parent),
      slantFactor: getSlantFactor(container, name),
      order: index + 1,
    })
  })

  const backgroundFields = getAlphaFields(context, container, parent)

  return new Bayfill({
    name: 'Imported',
    polygons,
    backgroundFields,
    ...parent,
  })
}

function getOverlayPolygon (context: Context, backgroundFacies: FaciesGroup, container: XMLElement, order: number, parent: Parent): OverlayPolygon {
  return new OverlayPolygon({
    group: backgroundFacies,
    center: getNumericValue(container, 'TruncIntervalCenter') || 0,
    field: getAlphaField(context, container.attributes.name, parent),
    fraction: getNumericValue(container, 'ProbFrac') || 0,
    facies: getFacies(context, getName(container, 'ProbFrac'), parent),
    order,
  })
}

async function getOverlayPolygons (context: Context, group: XMLElement, parent: Parent, offset = 0): Promise<OverlayPolygon[]> {
  const { dispatch } = context
  const backgroundFacies = await dispatch('facies/groups/get', {
    facies: getBackgroundFacies(context, group, parent),
    parent,
  }, { root: true })
  const _getOverlayPolygon = (el: XMLElement, index = 0): OverlayPolygon => getOverlayPolygon(context, backgroundFacies, el, offset + index + 1, parent)
  const polygons = ensureArray(getNodeValues(group, 'AlphaField'))
  return polygons.map(_getOverlayPolygon)
}

function hasElement (container: XMLElement, property: string): boolean {
  const naive = container[`${property}`]
  if (typeof naive === 'undefined' && hasOwnProperty(container, 'elements')) {
    return !!container.elements.find((el): boolean => el.name === property)
  }
  return !!naive
}

async function makeOverlayPolygons (context: Context, container: XMLElement, parent: Parent, offset = 0): Promise<OverlayPolygon[]> {
  const overlayPolygons = []
  if (hasElement(container, 'OverLayModel')) {
    const groups = ensureArray(getNodeValues(getMandatoryNodeValue(container, 'OverLayModel'), 'Group'))
    for (const group of groups) {
      const polygons: OverlayPolygon[] = await getOverlayPolygons(context, group, parent, overlayPolygons.length + offset)
      overlayPolygons.push(...polygons)
    }
  }
  return overlayPolygons
}

async function makeOverlayTruncationRule<P extends Polygon, T extends OverlayTruncationRule> (
  context: Context,
  container: XMLElement,
  parent: Parent,
  makeBackgroundPolygons: (container: XMLElement) => P[],
  _class: Newable<T>,
  extra = {},
): Promise<T> {
  const backgroundFields = getAlphaFields(context, container, parent)
  const backgroundPolygons = makeBackgroundPolygons(getMandatoryNodeValue(container, 'BackGroundModel'))

  const overlayPolygons = await makeOverlayPolygons(context, container, parent, backgroundPolygons.length)
  const polygons = [...backgroundPolygons, ...overlayPolygons]

  return new _class({
    name: 'Imported',
    backgroundFields,
    polygons,
    _useOverlay: overlayPolygons.length > 0,
    parent,
    ...extra,
  })
}

async function makeNonCubicTruncationRule (context: Context, container: XMLElement, parent: Parent): Promise<NonCubic> {
  function makeNonCubicBackgroundFacies (container: XMLElement): NonCubicPolygon[] {
    return getNodeValues(container, 'Facies').map((element, index): NonCubicPolygon => new NonCubicPolygon({
      angle: {
        value: getMandatoryNumericValue(element, 'Angle'),
        updatable: isFMUUpdatable(element, 'Angle'),
      },
      fraction: getMandatoryNumericValue(element, 'ProbFrac'),
      facies: getFacies(context, getName(element), parent),
      order: index + 1,
    }))
  }
  /* eslint-disable-next-line no-return-await */
  return await makeOverlayTruncationRule(
    context,
    container,
    parent,
    makeNonCubicBackgroundFacies,
    NonCubic,
  )
}

async function makeCubicTruncationRule (context: Context, container: XMLElement, parent: Parent): Promise<Cubic> {
  function getPolygon (element: XMLElement, order: number, root: Optional<CubicPolygon>, parent: Parent): CubicPolygon {
    return new CubicPolygon({
      parent: root,
      fraction: getNumericValue(element) || 0,
      facies: getFacies(context, getName(element), parent),
      order,
    })
  }
  function getChildren (container: XMLElement, root: Optional<CubicPolygon>): CubicPolygon[] {
    const polygons = []
    let order = 1

    if (!root && hasElement(container, 'L1')) {
      container = (getNodeValue(container, 'L1') as XMLElement)
      root = new CubicPolygon({ parent: root, order: -1 })
    }
    if (root) polygons.push(root)

    if (!container) return polygons
    for (const element of container.elements) {
      if (element.name === 'ProbFrac') {
        polygons.push(getPolygon(element, order, root, parent))
      } else if (/L[0-9]+/.exec(element.name)) {
        polygons.push(...getChildren(element, new CubicPolygon({ parent: root, order })))
      }
      order += 1
    }
    return polygons
  }

  /* eslint-disable-next-line no-return-await */
  return await makeOverlayTruncationRule(
    context,
    container,
    parent,
    (container: XMLElement): CubicPolygon[] => getChildren(container, null),
    Cubic,
    {
      direction: getDirection(container),
    }
  )
}

function getTrend (gaussFieldFromFile: XMLElement): Optional<Trend> {
  const container = getNodeValue(gaussFieldFromFile, 'Trend')
  if (!container) return null

  let type: Optional<TrendType> = null
  let trendContainer: Optional<XMLElement> = null
  const [LINEAR, ELLIPTIC, ELLIPTIC_CONE, HYPERBOLIC, RMS_PARAM, RMS_TRENDMAP] = (['LINEAR', 'ELLIPTIC', 'ELLIPTIC_CONE', 'HYPERBOLIC', 'RMS_PARAM', 'RMS_TRENDMAP'] as TrendType[])

  const types: { name: TrendType, prop: string }[] = [
    { name: LINEAR, prop: 'Linear3D' },
    { name: ELLIPTIC, prop: 'Elliptic3D' },
    { name: ELLIPTIC_CONE, prop: 'EllipticCone3D' },
    { name: HYPERBOLIC, prop: 'Hyperbolic3D' },
    { name: RMS_PARAM, prop: 'RMSParameter' },
    { name: RMS_TRENDMAP, prop: 'RMSTrendMap' },
  ]
  for (const { name, prop } of types) {
    if (hasElement((container as XMLElement), prop)) {
      type = name
      trendContainer = getNodeValue((container as XMLElement), prop)
      break
    }
  }
  if (!type) throw new APSError('No trend type was given, or it was illegal')
  if (!trendContainer) return null

  const options: TrendConfiguration = {
    use: true,
    type: type,
    relativeStdDev: getMandatoryNumericValue(gaussFieldFromFile, 'RelStdDev'),
    relativeStdDevUpdatable: isFMUUpdatable(gaussFieldFromFile, 'RelStdDev'),
  }
  if ([LINEAR, ELLIPTIC, ELLIPTIC_CONE, HYPERBOLIC].includes(type)) {
    options.azimuth = getMandatoryNumericValue(trendContainer, 'azimuth')
    options.azimuthUpdatable = isFMUUpdatable(trendContainer, 'azimuth')
    options.stackingDirection = getStackingDirection(trendContainer, 'directionStacking')
    options.stackAngle = getMandatoryNumericValue(trendContainer, 'stackAngle')
    options.stackAngleUpdatable = isFMUUpdatable(trendContainer, 'stackAngle')
  }
  if ([ELLIPTIC, ELLIPTIC_CONE, HYPERBOLIC].includes(type)) {
    options.curvature = getMandatoryNumericValue(trendContainer, 'curvature')
    options.curvatureUpdatable = isFMUUpdatable(trendContainer, 'curvature')
    options.originType = getOriginType(trendContainer, 'origintype')
    options.originX = getMandatoryNumericValue(trendContainer, 'origin_x')
    options.originXUpdatable = isFMUUpdatable(trendContainer, 'origin_x')
    options.originY = getMandatoryNumericValue(trendContainer, 'origin_y')
    options.originYUpdatable = isFMUUpdatable(trendContainer, 'origin_y')
  }
  if ([ELLIPTIC, HYPERBOLIC, ELLIPTIC_CONE].includes(type)) {
    options.originZ = getMandatoryNumericValue(trendContainer, 'origin_z_simbox')
    options.originZUpdatable = isFMUUpdatable(trendContainer, 'origin_z_simbox')
  }
  if ([ELLIPTIC_CONE, HYPERBOLIC].includes(type)) {
    options.migrationAngle = getMandatoryNumericValue(trendContainer, 'migrationAngle')
    options.migrationAngleUpdatable = isFMUUpdatable(trendContainer, 'migrationAngle')
    const relativeSize = getNumericValue(trendContainer, 'relativeSize')
    if (relativeSize !== null) options.relativeSize = relativeSize
    options.relativeSizeUpdatable = isFMUUpdatable(trendContainer, 'relativeSize')
  }
  if ([RMS_PARAM].includes(type)) {
    options.parameter = getTextValue(trendContainer, 'TrendParamName')
  }
  if ([RMS_TRENDMAP].includes(type)) {
    options.trendMapName = getTextValue(trendContainer, 'TrendMapName')
    options.trendMapZone = getTextValue(trendContainer, 'TrendMapZone')
  }

  return new Trend(options)
}

function getVariogram (gaussFieldFromFile: XMLElement): Variogram {
  const container = getMandatoryNodeValue(gaussFieldFromFile, 'Vario')
  const type = getName(container)
  const options: VariogramConfiguration = {
    type,
    // Angles
    azimuth: getMandatoryNumericValue(container, 'AzimuthAngle'),
    azimuthUpdatable: isFMUUpdatable(container, 'AzimuthAngle'),
    dip: getMandatoryNumericValue(container, 'DipAngle'),
    dipUpdatable: isFMUUpdatable(container, 'DipAngle'),
    // Ranges
    main: getMandatoryNumericValue(container, 'MainRange'),
    mainUpdatable: isFMUUpdatable(container, 'MainRange'),
    perpendicular: getMandatoryNumericValue(container, 'PerpRange'),
    perpendicularUpdatable: isFMUUpdatable(container, 'PerpRange'),
    vertical: getMandatoryNumericValue(container, 'VertRange'),
    verticalUpdatable: isFMUUpdatable(container, 'VertRange'),
  }
  if (type === 'GENERAL_EXPONENTIAL') {
    options.power = getMandatoryNumericValue(container, 'Power')
    options.powerUpdatable = isFMUUpdatable(container, 'Power')
  }
  return new Variogram(options)
}

async function getCrossSection ({ dispatch }: Context, parent: Parent): Promise<CrossSection> {
  // eslint-disable-next-line no-return-await
  return await dispatch('gaussianRandomFields/crossSections/fetch', parent, { root: true })
}

function getZoneNumber (zoneModel: XMLElement): number {
  const zoneNumber = parseInt(zoneModel.attributes.number, 10)
  return zoneNumber
}

function getMandatoryTextValue(element: XMLElement, keyword: string) {
  if (hasElement(element, keyword) ){
    return String(getTextValue(element, keyword))
  }
  throw new KeywordError(keyword)
}

const jobSettings = (apsModelContainer:XMLElement) => {
  const default_settings: JobSettingsParam = {
    runFmuWorkflows: false,
    onlyUpdateFromFmu: false,
    simulationGrid: 'ERTBOX',
    importFields: false,
    fieldFileFormat: 'roff',
    customTrendExtrapolationMethod: 'extend_layer_mean',
    exportFmuConfigFiles: false,
    onlyUpdateResidualFields: false,
    useNonStandardFmu: false,
    exportErtBoxGrid: true,
    maxAllowedFractionOfValuesOutsideTolerance: 0.1,
    toleranceOfProbabilityNormalisation: 0.2,
    transformType: 0,
    debugLevel: 1,
  }
  const jobSettingsElement = getNodeValue(apsModelContainer,'JobSettings')
  if (jobSettingsElement == null) {
    return default_settings
  }

  const fmuSettingsElement = getMandatoryNodeValue(jobSettingsElement,'FmuSettings')
  const fmuMode = getMandatoryTextValue(fmuSettingsElement, 'FmuMode')
  let updateGRFElement = null
  let ertBoxGrid = 'ERTBOX'
  let exchangeMode = false
  let fileFormat = 'roff'
  let extrapolationMethod = 'extend_layer_mean'
  let exportCheck = false
  let onlyResidual = false
  let useAPSConfigFile = false
  let exportErtBox = true
  if (fmuMode === 'FIELDS')
  {
    updateGRFElement = getMandatoryNodeValue(fmuSettingsElement,'UpdateGRF')
    ertBoxGrid = getMandatoryTextValue(updateGRFElement, 'ErtBoxGrid')
    exportErtBox = getMandatoryTextValue(updateGRFElement, 'ExportErtBoxGrid') === 'YES'
    exchangeMode = getMandatoryTextValue(updateGRFElement, 'ExchangeMode') === 'AUTO'
    fileFormat = getMandatoryTextValue(updateGRFElement, 'FileFormat')
    extrapolationMethod = getMandatoryTextValue(updateGRFElement, 'ExtrapolationMethod')
    exportCheck = getMandatoryTextValue(fmuSettingsElement, 'ExportConfigFiles') === 'YES'
    onlyResidual = getMandatoryTextValue(fmuSettingsElement, 'UseResidualFields') === 'YES'
    useAPSConfigFile = getMandatoryTextValue(fmuSettingsElement, 'UseNonStandardFMU') === 'YES'
  }
  if (fmuMode === 'NOFIELD')
  {
    exportCheck = getMandatoryTextValue(fmuSettingsElement, 'ExportConfigFiles') === 'YES'
    useAPSConfigFile = getMandatoryTextValue(fmuSettingsElement, 'UseNonStandardFMU') === 'YES'
  }

  const runSettingsElement = getMandatoryNodeValue(jobSettingsElement, 'RunSettings')
  const maxFractionNotNormalised = getMandatoryNumericValue(runSettingsElement, 'MaxFractionNotNormalised')
  const toleranceLimitProbability = getMandatoryNumericValue(runSettingsElement,'ToleranceLimitProbability')
  const transformationSettings = getMandatoryNumericValue(jobSettingsElement, 'TransformationSettings')
  const logSetting = getMandatoryNumericValue(jobSettingsElement, 'LogSetting')


  const settings: JobSettingsParam = {
    runFmuWorkflows: (fmuMode === 'FIELDS'), // might have to wrap !! around paranthesis to evaluate as false if fmuMode is undefined/null
    onlyUpdateFromFmu: (fmuMode === 'NOFIELDS'),
    simulationGrid: (fmuMode === 'FIELDS' && ertBoxGrid) ? ertBoxGrid : 'ERTBOX',
    importFields: (fmuMode === 'FIELDS') ? exchangeMode : false,
    fieldFileFormat: (fmuMode === 'FIELDS') ? fileFormat : 'roff',
    customTrendExtrapolationMethod: (fmuMode === 'FIELDS') ? extrapolationMethod : 'mean',
    exportFmuConfigFiles: (fmuMode === 'FIELDS' || fmuMode === 'NOFIELDS') ? exportCheck : false,
    onlyUpdateResidualFields: (fmuMode === 'FIELDS') ? onlyResidual : false,
    useNonStandardFmu: (fmuMode === 'FIELDS' || fmuMode === 'NOFIELDS') ? useAPSConfigFile : false,
    exportErtBoxGrid: (fmuMode === 'FIELDS') ? exportErtBox : false,
    maxAllowedFractionOfValuesOutsideTolerance: maxFractionNotNormalised ?? 0.1,
    toleranceOfProbabilityNormalisation: toleranceLimitProbability ?? 0.2,
    transformType: transformationSettings ?? 0,
    debugLevel: logSetting ?? 0,
  }

  return settings
}


const module: Module<Record<string, unknown>, RootState> = {
  namespaced: true,

  actions: {

    /**
     * This is the entry point for loading a model file
     * @param dispatch
     * @param commit
     * @param json
     * @param fileName
     * @returns {Promise<void>}
     */
    populateGUI: async ({ dispatch, commit }, { json, fileName }): Promise<void> => {
      const apsModelContainer = getNodeValue(JSON.parse(json), 'APSModel')
      if (!apsModelContainer) throw new APSError('The model is missing the keyword "APSModel"')

      await dispatch('parameters/names/model/select', fileName, { root: true })

      commit('LOADING', { loading: true, message: `Loading the model file, "${fileName}"` }, { root: true })

      const actions = [
        { action: 'parameters/names/workflow/select', property: 'RMSWorkflowName', check: true },
        { action: 'gridModels/select', property: 'GridModelName', check: false },
        { action: 'parameters/zone/select', property: 'ZoneParamName', check: true },
        { action: 'parameters/region/select', property: 'RegionParamName', check: true },
        { action: 'parameters/realization/select', property: 'ResultFaciesParamName', check: true },
      ]
      try {
        for (const { action, property, check } of actions) {
          if (check ? hasElement(apsModelContainer, property) : true) {
            await dispatch(action, getTextValue(apsModelContainer, property), { root: true })
          }
        }
        await dispatch('fmu/onlyUpdateFromFmu/set', json.includes('"kw":'), { root: true })

        const apsModels = getNodeValues(getMandatoryNodeValue(apsModelContainer, 'ZoneModels'), 'Zone')

        await dispatch('populateGlobalFaciesList', getNodeValue(apsModelContainer, 'MainFaciesTable'))

        await dispatch('populateJobSettings', apsModelContainer)

        const localActions = [
          'populateGaussianRandomFields',
          'populateFaciesProbabilities',
          'populateTruncationRules',
          'populateGridLayout',
          // Now we can select zones and regions on the left-hand side of the gui.
          'selectZonesAndRegions',
        ]
        for (const action of localActions) {
          await dispatch(action, apsModels)
        }
        await Promise.all([
          { type: 'settings', panel: 'truncationRule' },
          { type: 'preview', panel: 'truncationRuleMap' },
        ].map((payload): Promise<void> => dispatch('panels/open', payload, { root: true })))
      } catch (reason) {
        await displayMessage({ dispatch }, reason, 'error')
      } finally {
        commit('LOADING', { loading: false }, { root: true })
      }
    },

    populateGridLayout: async ({ dispatch, rootState, rootGetters }, apsModels: XMLElement[]): Promise<void> => {
      for (const apsModel of apsModels) {
        const gridLayout = getTextValue(apsModel, 'GridLayout')
        if (gridLayout) {
          const zoneNumber = getZoneNumber(apsModel)
          const { zone } = rootGetters['zones/byCode'](zoneNumber)
          await dispatch('zones/conformity', { zone, value: gridLayout }, { root: true })
        }
      }
    },

    /**
     * Takes the main facies table from a file and compares it to the facies log loaded from the project
     * (based on selected blocked well). Facies both loaded from the project and present in the file are
     * selected. Any facies not present in the project is added and then selected.
     * This method returns a promise. In order to let it complete fully before moving on, call it with async - await
     * @param dispatch
     * @param rootState
     * @param mainFaciesTableFromFile
     * @returns {Promise<void>}
     */
    populateGlobalFaciesList: async ({ dispatch, rootState }, mainFaciesTableFromFile): Promise<void> => {
      await dispatch('parameters/blockedWell/select', mainFaciesTableFromFile.attributes.blockedWell, { root: true })
      await dispatch('parameters/blockedWellLog/select', mainFaciesTableFromFile.attributes.blockedWellLog, { root: true })

      for (const faciesContainer of getNodeValues(mainFaciesTableFromFile, 'Facies')) {
        // facies information from the file.
        const name = getName(faciesContainer)
        const code = getNumericValue(faciesContainer, 'Code')

        // corresponding facies from project
        const facies = Object.values(rootState.facies.global.available)
          .find((facies): boolean => facies.name === name && facies.code === code)

        // logic for selecting / adding
        if (!facies) {
          await dispatch('facies/global/new', { code, name }, { root: true })
        }
      }
    },

    /**
     * This is the part that selects zones and regions combinations present in the file.
     * @param dispatch
     * @param rootState
     * @param zoneModelsFromFile
     */
    selectZonesAndRegions: async ({ dispatch, rootState }, zoneModelsFromFile: XMLElement[]): Promise<void> => {
      // synthesizing zones and region info: Zones and regions could be specified in weird ways. For instance, we could
      // have zones regions defined in the input data as
      //  zone 1, region 2
      //  zone 2, region 3
      //  zone 1, region 3
      //  zone 1, region 1
      //  etc
      // Therefore we loop through all zones and regions collecting a map with given zones as keys and
      // regions for each zone a list of all regions.
      // This map is then used when selecting zones and regions later
      const zoneRegionsMap = new Map()
      zoneModelsFromFile.forEach((zoneModel): void => {
        const zoneNumber = getZoneNumber(zoneModel)
        const regionNumber = zoneModel.attributes.regionNumber
        if (!zoneRegionsMap.has(zoneNumber)) {
          zoneRegionsMap.set(zoneNumber, [])
        }
        if (regionNumber) {
          zoneRegionsMap.get(zoneNumber).push(parseInt(regionNumber, 10))
        }
      })

      // checking that all zones and regions from the file is present/loaded from the project and selecting them as we
      // go. After finding everything that should be selected, we call the actual methods that sets the selected status
      // in the store.
      let zoneToSetAsCurrent
      let regionToSetAsCurrent
      const zonesToSelect = []
      const regionsToSelect = []

      for (const zoneRegionsItem of zoneRegionsMap) {
        const zoneIdFromFile = zoneRegionsItem[0]
        let zoneFound = false
        for (const id in rootState.zones.available) {
          const zone = rootState.zones.available[`${id}`]
          if (zone.code === zoneIdFromFile) {
            zoneFound = true
            zonesToSelect.push(zone)
            if (!zoneToSetAsCurrent) {
              zoneToSetAsCurrent = zone
            }
            const regionsInZone = zoneRegionsItem[1]
            for (let i = 0; i < regionsInZone.length; i++) {
              const regionIdFromFile = regionsInZone[`${i}`]
              let regionFound = false
              for (const regionId in zone.regions) {
                const region = rootState.zones.available[`${id}`].regions[`${regionId}`]
                if (region.code === regionIdFromFile) {
                  regionFound = true
                  if (!regionToSetAsCurrent) {
                    // This is the first region to be selected and will be marked as current region. In order for this to
                    // be visible/consistent, the parent zone must also be "current". Therefore we overwrite zoneToSetASCurrent
                    zoneToSetAsCurrent = zone
                    regionToSetAsCurrent = region
                  }
                  regionsToSelect.push(region)
                  // no need to loop through the rest of the zones´ regions.
                  break
                }
              }
              if (!regionFound) {
                // The file specified a zone with a region that does not exist in the project
                // we should ideally not be able to get here, as long as the file has been instantiated as an APS model
                // using the python code
                throw new Error(`The input file has at least one region (region ${regionIdFromFile} for zone ${zoneIdFromFile} ) not specified in the current project`)
              }
            }
            break
          }
        }
        if (!zoneFound) {
          // The file specified a zone that does not exist in the project
          // we should ideally not be able to get here, as long as the file has been instantiated as an APS model
          // using the python code
          throw new Error(`The input file has at least one zone (zone ${zoneIdFromFile}) not specified in the current project`)
        }
      }
      // if we get here, the data is ok, we have identified what to select and can make the selection
      await dispatch('zones/current', zoneToSetAsCurrent, { root: true })
      await dispatch('zones/select', zonesToSelect, { root: true })
      await Promise.all(zonesToSelect.map(zone => dispatch('zones/touch', { zone }, { root: true })))
      if (regionToSetAsCurrent) {
        await dispatch('regions/current', regionToSetAsCurrent, { root: true })
        await dispatch('regions/select', regionsToSelect, { root: true })
        await Promise.all(regionsToSelect.map(region => dispatch('regions/touch', region, { root: true })))
      }
    },

    /**
     * This adds and sets up the gaussian random fields specified in the file.
     * @param context
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateGaussianRandomFields: async (context, zoneModelsFromFile): Promise<void> => {
      const { dispatch } = context
      for (const zoneModel of zoneModelsFromFile) {
        const parent = getParent(context, zoneModel)

        for (const gaussFieldFromFile of getNodeValues(zoneModel, 'GaussField')) {
          await dispatch('gaussianRandomFields/add',
            new GaussianRandomField({
              name: gaussFieldFromFile.attributes.name,
              variogram: getVariogram(gaussFieldFromFile),
              trend: getTrend(gaussFieldFromFile),
              crossSection: await getCrossSection(context, parent),
              seed: hasElement(gaussFieldFromFile, 'SeedForPreview')
                ? getNumericValue(gaussFieldFromFile, 'SeedForPreview')
                : null,
              ...parent,
            }),
            { root: true }
          )
        }
      }
    },

    /**
     * Sets the facies probability for facies in zone. If the file specifies probCubes, the method sets the
     * probability to 1/number of fields in order to have the truncation rule visible after load
     * Note:
     * This will have to be updated in order to set correct selection based on zone/region.
     * as it is now it just updates the facies over and over again for each zone/region combo
     *
     * @param context
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateFaciesProbabilities: async (context, zoneModelsFromFile): Promise<void> => {
      const { dispatch, rootState } = context
      for (const zoneModel of zoneModelsFromFile) {
        const useConstantProb = getBooleanValue(zoneModel, 'UseConstProb')
        const parent = getParent(context, zoneModel)
        // TODO: handle SimBoxThickness (must await implementation from Sindre on this?)
        for (const faciesModel of getNodeValues(getMandatoryNodeValue(zoneModel, 'FaciesProbForModel'), 'Facies')) {
          const facies = await dispatch('facies/add', {
            facies: /* global */ Object.values(rootState.facies.global.available).find((obj): boolean => obj.name === getName(faciesModel)),
            parent,
          }, { root: true })
          await dispatch('facies/setConstantProbability', { parentId: facies.parentId, toggled: useConstantProb }, { root: true })
          if (useConstantProb) {
            await dispatch('facies/updateProbability', {
              facies,
              probability: getNumericValue(faciesModel, 'ProbCube')
            }, { root: true })
          } else {
            const probabilityCube = getTextValue(faciesModel, 'ProbCube')
            await dispatch('facies/changeProbabilityCube', { facies, probabilityCube }, { root: true })
          }
        }
        if (!useConstantProb) {
          await dispatch(
            'facies/averageProbabilityCubes',
            {
              zoneNumber: parent.zone.code,
              useRegions: !!parent.region,
              regionNumber: parent.region && parent.region.code,
            },
            { root: true }
          )
        }
      }
    },

    /**
     * Sets up Truncation Rules and connects them to fields as specified in the model file.
     * @param context
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateTruncationRules: async (context, zoneModelsFromFile): Promise<void> => {
      const { dispatch, commit, rootState } = context
      for (const zoneModel of zoneModelsFromFile) {
        const parent = getParent(context, zoneModel)

        if (hasElement(zoneModel, 'TruncationRule')) {
          const truncationRuleContainer = getMandatoryNodeValue(zoneModel, 'TruncationRule')
          let type = ''
          let rule = null
          if (hasElement(truncationRuleContainer, 'Trunc3D_Bayfill')) {
            type = 'Bayfill'
            rule = makeBayfillTruncationRule(context, getMandatoryNodeValue(truncationRuleContainer, 'Trunc3D_Bayfill'), parent)
          } else if (hasElement(truncationRuleContainer, 'Trunc2D_Angle')) {
            type = 'Non-Cubic'
            rule = await makeNonCubicTruncationRule(context, getMandatoryNodeValue(truncationRuleContainer, 'Trunc2D_Angle'), parent)
          } else {
            type = 'Cubic'
            rule = await makeCubicTruncationRule(context, getMandatoryNodeValue(truncationRuleContainer, 'Trunc2D_Cubic'), parent)
          }
          if (rule) {
            // now we should have everything needed to add the truncationRule.
            await dispatch('truncationRules/add', rule, { root: true })
          }

          // Changing presents must be done after the truncation rule is added (the command above must run to completion)
          commit(
            'truncationRules/preset/CHANGE_TYPE',
            {
              type: Object.values(rootState.truncationRules.templates.types.available)
                .find((item): boolean => item.name === type)
            },
            { root: true })
          commit('truncationRules/preset/CHANGE_TEMPLATE', { template: { text: 'Imported' } }, { root: true })
        }
      }
    },

    populateJobSettings: async (context, apsModelContainer: XMLElement): Promise<void> => {
      const { dispatch } = context
      const jobSettingsParam = jobSettings(apsModelContainer)
      await dispatch('fmu/runFmuWorkflows/set', jobSettingsParam.runFmuWorkflows, { root: true })
      await dispatch('fmu/onlyUpdateFromFmu/set', jobSettingsParam.onlyUpdateFromFmu, { root: true })
      // Update JobSettings window for the three cases:
      // Run APS facies update in AHM/ERT: runFmuWorkflows = True, onlyUpdateFromFmu = False
      // Only run uncertainty update:      runFmuWorkflows = False, onlyUpdateFromFmu = True
      // No FMU mode:                      runFmuWorkflows = False, onlyUpdateFromFmu = False
      // The last combination should not be used
      //where runFmuWorkflows = True and onlyUpdateFromFmu = True

      await dispatch('fmu/simulationGrid/set', jobSettingsParam.simulationGrid, { root: true })
      await dispatch('fmu/fieldFileFormat/set', jobSettingsParam.fieldFileFormat, { root: true })
      await dispatch('fmu/customTrendExtrapolationMethod/set', jobSettingsParam.customTrendExtrapolationMethod, { root: true })
      await dispatch('fmu/onlyUpdateResidualFields/set', jobSettingsParam.onlyUpdateResidualFields, { root: true })
      await dispatch('fmu/useNonStandardFmu/set', jobSettingsParam.useNonStandardFmu, { root: true })
      await dispatch('fmu/exportErtBoxGrid/set', jobSettingsParam.exportErtBoxGrid, { root: true })
      await dispatch('options/importFields/set', jobSettingsParam.importFields, { root: true })
      await dispatch('options/exportFmuConfigFiles/set', jobSettingsParam.exportFmuConfigFiles, { root: true })
      await dispatch('parameters/maxAllowedFractionOfValuesOutsideTolerance/select', jobSettingsParam.maxAllowedFractionOfValuesOutsideTolerance, { root: true })
      await dispatch('parameters/toleranceOfProbabilityNormalisation/select', jobSettingsParam.toleranceOfProbabilityNormalisation, { root: true })
      await dispatch('parameters/transformType/select', jobSettingsParam.transformType, { root: true })
      await dispatch('parameters/debugLevel/select', jobSettingsParam.debugLevel, { root: true })
    }

  },
}

export default module
