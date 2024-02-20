import { acceptHMRUpdate, defineStore } from 'pinia'

import type { Newable } from '@/utils/domain/bases/interfaces'
import APSError from '@/utils/domain/errors/base'
import type FaciesGroup from '@/utils/domain/facies/group'
import GaussianRandomField, {
  Variogram,
  Trend,
} from '@/utils/domain/gaussianRandomField'
import type {
  Facies,
  Polygon,
  Parent,
  GlobalFacies,
} from '@/utils/domain'
import {
  Bayfill,
  BayfillPolygon,
  NonCubic,
  NonCubicPolygon,
  Cubic,
  CubicPolygon,
  OverlayPolygon
} from '@/utils/domain'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'
import type CrossSection from '@/utils/domain/gaussianRandomField/crossSection'
import type {
  TrendConfiguration,
} from '@/utils/domain/gaussianRandomField/trend'
import type { VariogramConfiguration } from '@/utils/domain/gaussianRandomField/variogram'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import type { Optional } from '@/utils/typing'
import { usePanelStore } from '@/stores/panels'
import type {
  BayfillFacies,
  SlantFactorFacies
} from '@/utils/domain/polygon/bayfill'
import {
  requireSlantFactor
} from '@/utils/domain/polygon/bayfill'
import { useZoneStore } from '@/stores/zones'
import { useFaciesStore } from '@/stores/facies'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'
import { useParameterNameModelStore } from '@/stores/parameters/names/model'
import { useRootStore } from '@/stores'
import { useParameterNameWorkflowStore } from '@/stores/parameters/names/workflow'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterZoneStore } from '@/stores/parameters/zone'
import { useParameterRegionStore } from '@/stores/parameters/region'
import { useParameterRealizationStore } from '@/stores/parameters/realization'
import type { FieldFormats, TrendExtrapolationMethod } from '@/stores/fmu/options'
import { useFmuOptionStore } from '@/stores/fmu/options'
import { useFaciesGlobalStore } from '@/stores/facies/global'
import { displayMessage } from '@/utils/helpers/storeInteraction'
import type Zone from '@/utils/domain/zone'
import { isValidConformity, type Region } from '@/utils/domain/zone'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { isArray, isNumber } from 'lodash';
import { useRegionStore } from '@/stores/regions'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'
import { useTruncationRuleTemplateTypeStore } from '@/stores/truncation-rules/templates/types'
import { useOptionStore } from '@/stores/options'
import {
  useParametersMaxFractionOfValuesOutsideToleranceStore,
  useParametersToleranceOfProbabilityNormalisationStore
} from '@/stores/parameters/tolerance'
import type { TransformType } from '@/stores/parameters/transform-type'
import { isTransformType, useParameterTransformTypeStore } from '@/stores/parameters/transform-type'
import type { DebugLevel } from '@/stores/parameters/debug-level'
import { isDebugLevel, useParameterDebugLevelStore } from '@/stores/parameters/debug-level'
import type { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import type { ProbabilityCube } from '@/utils/domain/facies/local'

interface JobSettingsParam {
  runFmuWorkflows: boolean
  onlyUpdateFromFmu: boolean
  simulationGrid: string
  importFields: boolean
  fieldFileFormat: FieldFormats
  customTrendExtrapolationMethod: string
  exportFmuConfigFiles: boolean
  onlyUpdateResidualFields: boolean
  useNonStandardFmu: boolean
  exportErtBoxGrid: boolean
  maxAllowedFractionOfValuesOutsideTolerance: number
  toleranceOfProbabilityNormalisation: number
  transformType: TransformType
  debugLevel: DebugLevel
}

class KeywordError extends APSError {
  public constructor(keyword: string) {
    super(`The keyword, '${keyword}' is missing`)
  }
}

function ensureArray<T>(value: T | T[]): T[] {
  return Array.isArray(value) ? value : [value]
}

function getMandatoryNodeValue<T extends object, P extends keyof T>(
  container: T,
  prop: P,
): Exclude<T[P], undefined> {
  const value = container[prop]
  if (!value) throw new KeywordError(prop as string)
  return value as Exclude<T[P], undefined>
}

function getName(container: { '@_name': string }): string {
  return container['@_name'].trim()
}

function getTextValue<T extends object>(
  elem: T | string,
  prop: Optional<keyof T> = null,
): Optional<string> {
  let value: unknown = elem
  if (prop) {
    if (typeof elem === 'string') {
      throw new TypeError('prop cannot be used with a string as element')
    }
    value = elem[prop]
  }
  // The parser we use (fast-xml-parser) will give numbers if they appear in a text node
  if (!value && value !== 0) return null
  if (typeof value === 'string') return value.trim()
  try {
    if (typeof value === 'object' && '#text' in value) {
      value = (value['#text'] as string)
    }
  } catch {
    // ignore, as the `in` operator throws an error when used on non-objects
    // also; typeof null === 'object', which will also throw an error
  }
  if (typeof value === 'string') return value.trim()
  if (value || value === 0) return String(value)
  return null
}

function getOriginType<T extends object>(
  elem: T,
  prop: Optional<keyof T> = null,
): 'RELATIVE' | 'ABSOLUTE' {
  let value = getTextValue(elem, prop)
  if (value) {
    value = value.replace(/'/g, '').toUpperCase()
    if (!['RELATIVE', 'ABSOLUTE'].includes(value))
      throw new APSError(
        `The origin typ MUST be one of "RELATIVE", or "ABSOLUTE", but was ${value}`,
      )
  }
  return value as 'RELATIVE' | 'ABSOLUTE'
}

function isFMUUpdatable<T extends object>(
  elem: MaybeFmuUpdatable | T,
  prop: Optional<keyof T> = null,
): boolean {
  let value = elem
  if (prop) {
    value = (elem as T)[prop] as MaybeFmuUpdatable
  }
  if (typeof value === 'number') return false
  return !!(value && '@_kw' in value && value["@_kw"])
}

function getNumericValue<T extends object>(
  elem: T,
  prop: Optional<keyof T> = null,
): Optional<number> {
  const text = getTextValue(elem, prop)
  if (text) {
    return Number(text)
  }
  return null
}

function getMandatoryNumericValue<T extends number, Obj extends object>(elem: Obj, prop: keyof Obj, guard?: (value: number) => value is T): T {
  const value = getNumericValue(elem, prop)
  if (value === null) throw new KeywordError(prop as string)
  if (guard && !guard(value)) throw new Error(`'${prop as string}' has an illegal value`)
  return value as T
}

function getBooleanValue<T extends object>(
  elem: T,
  prop: Optional<keyof T> = null,
): Optional<boolean> {
  const value = getNumericValue(elem, prop)
  if (value || value === 0) {
    return Boolean(value)
  }
  return null
}

function getStackingDirection<Trend extends { directionStacking: -1 | 1 }>(
  elem: Trend,
): 'PROGRADING' | 'RETROGRADING' {
  const direction = elem.directionStacking
  if (direction === 1) {
    return 'PROGRADING'
  }
  if (direction === -1) {
    return 'RETROGRADING'
  }
  throw new APSError('Stacking direction is defined incorrectly for trend')
}

function getParent(zoneModel: ZoneModelContentItem): Parent {
  const zoneStore = useZoneStore()
  const zoneNumber = parseInt(zoneModel['@_number'], 10)
  const regionNumber = zoneModel['@_regionNumber']
    ? parseInt(zoneModel['@_regionNumber'], 10)
    : null
  return zoneStore.byCode(zoneNumber, regionNumber)
}

function getFacies(
  name: string,
  parent: Parent,
): Facies | undefined {
  const { available } = useFaciesStore()
  return (available as Facies[])
    .filter((facies): boolean => facies.isChildOf(parent))
    .find((facies): boolean => facies.name === name)
}

function getBackgroundFacies(
  container: TruncationRuleOverlayModelGroupContent,
  parent: Parent,
): Facies[] {
  const over = ensureArray(container.BackGround)

  const backgroundFacies: Facies[] = []
  for (const el of over) {
    const name = getTextValue(el)
    if (name === null) throw new APSError('A Facies had no name')
    const facies = getFacies(name, parent)
    if (facies) backgroundFacies.push(facies)
  }
  return backgroundFacies
}

type ExpectedBayfillFaciesNames = Exclude<BayfillFacies, 'Bayhead Delta' | 'Wave influenced Bayfill'> | 'BHD' | 'WBF'

function getFaciesFromBayfill(
  container: TruncationRuleContentBayfill,
  item: ExpectedBayfillFaciesNames | BayfillFacies,
  parent: Parent,
): Facies {
  switch (item) {
    case 'Bayhead Delta':
      item = 'BHD'
      break
    case 'Wave influenced Bayfill':
      item = 'WBF'
      break
  }
  const backgroundModel = getMandatoryNodeValue(container, 'BackGroundModel')

  const name = backgroundModel[item]
  if (!name) throw new APSError('The polygon does not have a Facies')

  const facies = getFacies(name, parent)
  if (!facies)
    throw new APSError('The Facies has not been added to the internal state')

  return facies
}

type ExpectedSlantFactorKeys = 'SF' | 'YSF' | 'SBHD'

function getSlantFactorKey(facies: SlantFactorFacies): ExpectedSlantFactorKeys | null {
    switch (facies) {
      case 'Floodplain':
        return  'SF'
      case "Subbay":
        return  'YSF'
      case "Bayhead Delta":
        return  'SBHD'
      default:
        return null
  }
}


function getSlantFactor(
  container: TruncationRuleContentBayfill,
  item: SlantFactorFacies,
): FmuUpdatableValue {

  const key = getSlantFactorKey(item)
  if (key === null) throw new KeywordError(item)
  const element = getMandatoryNodeValue(container, 'BackGroundModel')
  return new FmuUpdatableValue({
          value: getMandatoryNumericValue(element, key),
          updatable: isFMUUpdatable(element, key),
    })
}

function getAlphaField(
  name: string,
  parent: Parent,
): GaussianRandomField {
  const { available } = useGaussianRandomFieldStore()
  const field = Object.values(available as GaussianRandomField[])
    .filter((field): boolean => field.isChildOf(parent))
    .find((field): boolean => field.name === name)
  if (!field)
    throw new APSError(
      `The Gaussian Random Field, with name ${name}, and parent; ${parent} does not exist`,
    )
  return field
}

type AlphaFieldsContent = {
  BackGroundModel: {
    AlphaFields: string
  }
}

function getAlphaFields(
  container: AlphaFieldsContent,
  parent: Parent,
): GaussianRandomField[] {
  const alphaFields = getTextValue(
    getMandatoryNodeValue(container, 'BackGroundModel'),
    'AlphaFields',
  )
  if (alphaFields === null) throw new KeywordError('AlphaFields')
  return alphaFields
    .split(' ')
    .map(
      (name: string): GaussianRandomField =>
        getAlphaField(name, parent),
    )
}

function getDirection(container: TruncationRuleContentCubic): 'V' | 'H' {
  return getMandatoryNodeValue(
    getMandatoryNodeValue(container, 'BackGroundModel'),
    'L1',
  )['@_direction']
}

function makeBayfillTruncationRule(
  container: TruncationRuleContentBayfill,
  parent: Parent,
): Bayfill {
  const names = [
    'Floodplain',
    'Subbay',
    'Wave influenced Bayfill',
    'Bayhead Delta',
    'Lagoon',
  ] as BayfillFacies[]
  const polygons = names.map((name, index): BayfillPolygon => {
    const facies = getFaciesFromBayfill(container, name, parent)
    const order = index + 1
    return requireSlantFactor(name)
    ? new BayfillPolygon(({
        name,
        facies,
        slantFactor: getSlantFactor(container, name),
        order
      }))
      : new BayfillPolygon({
        name,
        facies,
        order
      })
  })

  const backgroundFields = getAlphaFields(container, parent)

  return new Bayfill({
    name: 'Imported',
    polygons,
    backgroundFields,
    ...parent,
  })
}

function getOverlayPolygon(
  backgroundFacies: FaciesGroup,
  container: TruncationRuleOverlayModelGroupContent['AlphaField'][number],
  order: number,
  parent: Parent,
): OverlayPolygon {
  return new OverlayPolygon({
    group: backgroundFacies,
    center: getNumericValue(container, 'TruncIntervalCenter') || 0,
    field: getAlphaField(getName(container), parent),
    fraction: getNumericValue(container, 'ProbFrac') || 0,
    facies: getFacies(getName(container.ProbFrac), parent),
    order,
  })
}

function getOverlayPolygons(
  group: TruncationRuleOverlayModelGroupContent,
  parent: Parent,
  offset = 0,
): OverlayPolygon[] {
  const { get } = useFaciesGroupStore()
  const backgroundFacies = get(getBackgroundFacies(group, parent), parent)
  const polygons = ensureArray(group.AlphaField)
  return polygons.map((el, index) => getOverlayPolygon(backgroundFacies, el, offset + index + 1, parent))
}

function makeOverlayPolygons(
  container: TruncationRuleContentOverlay,
  parent: Parent,
  offset = 0,
): OverlayPolygon[] {
  const overlayPolygons = []
  if ('OverLayModel' in container) {
    const groups = ensureArray((getMandatoryNodeValue(container, 'OverLayModel').Group))
    for (const group of groups) {
      const polygons: OverlayPolygon[] = getOverlayPolygons(
        group,
        parent,
        overlayPolygons.length + offset,
      )
      overlayPolygons.push(...polygons)
    }
  }
  return overlayPolygons
}

type TruncationRuleContentOverlay = TruncationRuleContentNonCubic | TruncationRuleContentCubic

function makeOverlayTruncationRule<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P>,
  CONTAINER extends TruncationRuleContentOverlay
>(
  container: CONTAINER,
  parent: Parent,
  makeBackgroundPolygons: (container: CONTAINER['BackGroundModel']) => T[],
  _class: Newable<RULE>,
  extra = {},
): RULE {
  const backgroundFields = getAlphaFields(container, parent)
  const backgroundPolygons = makeBackgroundPolygons(
    getMandatoryNodeValue(container, 'BackGroundModel'),
  )

  const overlayPolygons = makeOverlayPolygons(
    container,
    parent,
    backgroundPolygons.length,
  )
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

function makeNonCubicTruncationRule(
  container: TruncationRuleContentNonCubic,
  parent: Parent,
): NonCubic {
  function makeNonCubicBackgroundFacies(
    container: TruncationRuleContentNonCubic['BackGroundModel'],
  ): NonCubicPolygon[] {
    return (container.Facies).map(
      (element, index): NonCubicPolygon =>
        new NonCubicPolygon({
          angle: {
            value: getMandatoryNumericValue(element, 'Angle'),
            updatable: isFMUUpdatable(element, 'Angle'),
          },
          fraction: getMandatoryNumericValue(element, 'ProbFrac'),
          facies: getFacies(getName(element), parent),
          order: index + 1,
        }),
    )
  }
  return makeOverlayTruncationRule(
    container,
    parent,
    makeNonCubicBackgroundFacies,
    NonCubic,
  )
}

function makeCubicTruncationRule(
  container: TruncationRuleContentCubic,
  parent: Parent,
): Cubic {
  type NodeTag = Attributes<{
    id: string
    parentId: string
    order: string
  }>
  function flattenHierarchy(container: TruncationRuleContentCubic['BackGroundModel']): (ProcessedProbabilityFraction | NodeTag)[] {
    const elements: (ProcessedProbabilityFraction | NodeTag)[] = []
    const items = Object.values(container.L1).flat()

    elements.push({
      '@_id': container.L1['@_id'],
      '@_parentId': '',
      '@_order': '-1',
    })

    while (items.length > 0) {
      const item = items.pop()
      if (typeof item === 'string') {
        continue
      } else if (isArray(item)) {
        elements.push(...(items as ProcessedProbabilityFraction[]))
      } else if ('#text' in item) {
        elements.push(item)
      } else {
        elements.push({
          '@_id': item['@_id'],
          '@_parentId': item['@_parentId'],
          '@_order': item['@_order'],
        } as NodeTag)
        items.push(...Object.values(item).flat())
      }
    }

    return elements
      .sort((a, b) => {
        return parseInt(a['@_order'], 10) - parseInt(b['@_order'], 10)
      })
  }

  function getChildren(
    container: TruncationRuleContentCubic['BackGroundModel'],
  ): CubicPolygon[] {
    // Flatten the hierarchy
    const flattened = flattenHierarchy(container)
    const polygons: CubicPolygon[] = []
    const parents = flattened.reduce((nodes, polygon) => {
      if ('@_id' in polygon) {
        if (polygon['@_parentId'] && !(polygon['@_parentId'] in nodes)) {
          const parent = new CubicPolygon({
            parent: null, // Not known at the moment
            order: parseInt(polygon['@_order'], 10),
            id: polygon['@_parentId'],
          })
          nodes[parent.id] = parent
        }
        if (!(polygon['@_id'] in nodes)) {
          const parent = nodes[polygon['@_parentId']]
          nodes[polygon['@_id']] = new CubicPolygon({
            parent,
            order: parseInt(polygon['@_order'], 10),
            id: polygon['@_id'],
          })
        }
      }
      return nodes
    }, {} as Record<string, CubicPolygon>)

    polygons.push(...Object.values(parents))

    flattened.forEach((polygon) => {
      if ('#text' in polygon) {
          polygons.push(new CubicPolygon({
            parent: parents[polygon['@_parentId']],
            fraction: getNumericValue(polygon) || 0,
            facies: getFacies(getName(polygon), parent),
            order: parseInt(polygon['@_order'], 10),
          }))
      }
    })

    // Ensure each level / group have an order between 1 and the number of siblings
    polygons.forEach(parent => {
      if (parent.children.length > 0){
        const orderMapping = parent.children
          .map(child => child.order)
          .sort((a, b) => a - b)
          .reduce((mapping, child, index) => ({
            ...mapping,
          [child]: index + 1
        }), {} as Record<number, number>)

        parent.children.forEach(child => {
          child.order = orderMapping[child.order]
        })
      }
    })

    if (polygons.filter(({ parent }) => parent === null).length !== 1) {
      console.error(polygons.filter(({ parent}) => parent === null))
      throw new APSError('The truncation rule does not have as unique root')
    }
    return polygons
  }

  return makeOverlayTruncationRule(
    container,
    parent,
    (container): CubicPolygon[] => getChildren(container),
    Cubic,
    {
      direction: getDirection(container),
    },
  )
}

type TrendDescription = {
  type: 'LINEAR',
  container: LinearTrend
} | {
  type: 'ELLIPTIC',
  container: EllipticTrend,
} | {
  type: 'ELLIPTIC_CONE',
  container: EllipticConeTrend,
} | {
  type: 'HYPERBOLIC',
  container: HyperbolicTrend,
} | {
  type: 'RMS_PARAM',
  container: RMSParameterTrend,
} | {
  type: 'RMS_TRENDMAP',
  container: RMSTrendMapTrend,
}

function extractTrend(container: ZoneModelGaussFieldContent['Trend']): TrendDescription {
  if ('Linear3D' in container) {
    return {
      type: 'LINEAR',
      container: container.Linear3D,
    }
  } else if ('Elliptic3D' in container) {
    return {
      type: 'ELLIPTIC',
      container: container.Elliptic3D,
    }
  } else if ('EllipticCone3D' in container) {
    return {
      type: 'ELLIPTIC_CONE',
      container: container.EllipticCone3D,
    }
  } else if ('Hyperbolic3D' in container) {
    return {
      type: 'HYPERBOLIC',
      container: container.Hyperbolic3D,
    }
  } else if ('RMSParameter' in container) {
    return {
      type: 'RMS_PARAM',
      container: container.RMSParameter
    }
  } else if ('RMSTrendMap' in container) {
    return {
      type: 'RMS_TRENDMAP',
      container: container.RMSTrendMap,
    }
  } else {
    throw new APSError('No trend type was given, or it was illegal')
  }
}

function getTrend(gaussFieldFromFile: ZoneModelGaussFieldContent): Optional<Trend> {
  const container = gaussFieldFromFile.Trend
  if (!container) return null

  const { type, container: trendContainer } = extractTrend(container)

  const options: TrendConfiguration = {
    use: true,
    type: type,
    relativeStdDev: getMandatoryNumericValue(gaussFieldFromFile, 'RelStdDev'),
    relativeStdDevUpdatable: isFMUUpdatable(gaussFieldFromFile, 'RelStdDev'),
  }
  if ('azimuth' in trendContainer) {
    options.azimuth = getMandatoryNumericValue(trendContainer, 'azimuth')
    options.azimuthUpdatable = isFMUUpdatable(trendContainer, 'azimuth')
    options.stackingDirection = getStackingDirection(trendContainer)
    options.stackAngle = getMandatoryNumericValue(trendContainer, 'stackAngle')
    options.stackAngleUpdatable = isFMUUpdatable(trendContainer, 'stackAngle')
  }
  if ('curvature' in trendContainer) {
    options.curvature = getMandatoryNumericValue(trendContainer, 'curvature')
    options.curvatureUpdatable = isFMUUpdatable(trendContainer, 'curvature')
    options.originType = getOriginType(trendContainer, 'origintype')
    options.originX = getMandatoryNumericValue(trendContainer, 'origin_x')
    options.originXUpdatable = isFMUUpdatable(trendContainer, 'origin_x')
    options.originY = getMandatoryNumericValue(trendContainer, 'origin_y')
    options.originYUpdatable = isFMUUpdatable(trendContainer, 'origin_y')
    options.originZ = getMandatoryNumericValue(
      trendContainer,
      'origin_z_simbox',
    )
    options.originZUpdatable = isFMUUpdatable(trendContainer, 'origin_z_simbox')
  }
  if ('migrationAngle' in trendContainer) {
    options.migrationAngle = getMandatoryNumericValue(
      trendContainer,
      'migrationAngle',
    )
    options.migrationAngleUpdatable = isFMUUpdatable(
      trendContainer,
      'migrationAngle',
    )
    const relativeSize = getNumericValue(trendContainer, 'relativeSize')
    if (relativeSize !== null) options.relativeSize = relativeSize
    options.relativeSizeUpdatable = isFMUUpdatable(
      trendContainer,
      'relativeSize',
    )
  }
  if ('TrendParamName' in trendContainer) {
    options.parameter = getTextValue(trendContainer, 'TrendParamName')
  }
  if ('TrendMapName' in trendContainer) {
    options.trendMapName = getTextValue(trendContainer, 'TrendMapName')
    options.trendMapZone = getTextValue(trendContainer, 'TrendMapZone')
  }

  return new Trend(options)
}

function getVariogram(gaussFieldFromFile: ZoneModelGaussFieldContent): Variogram {
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

function getCrossSection(
  parent: Parent,
): CrossSection | null {
  const { fetch } = useGaussianRandomFieldCrossSectionStore()
  return fetch(parent.zone, parent.region)
}

function getZoneNumber(zoneModel: ZoneModelContentItem): number {
  const zoneNumber = parseInt(zoneModel['@_number'], 10)
  return zoneNumber
}

function getMandatoryTextValue<T extends object>(element: T, keyword: keyof T): T[keyof T] | string {
  if (keyword in element) {
    return String((element[keyword] as string).trim())
  }
  throw new KeywordError(keyword as string)
}

const jobSettings = (apsModelContainer: APSModelContent, modelFileContainsFmuSettings: boolean) => {
  const default_settings: JobSettingsParam = {
    runFmuWorkflows: false,
    onlyUpdateFromFmu: modelFileContainsFmuSettings,
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
  const jobSettingsElement = apsModelContainer.JobSettings
  if (jobSettingsElement == null) {
    return default_settings
  }

   const fmuSettingsElement = getMandatoryNodeValue(
    jobSettingsElement,
    'FmuSettings',
  )
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
  switch (fmuMode) {
    case "FIELDS":
      updateGRFElement = getMandatoryNodeValue(fmuSettingsElement, 'UpdateGRF')
      ertBoxGrid = getMandatoryTextValue(updateGRFElement, 'ErtBoxGrid')
      exportErtBox =
        getTextValue(updateGRFElement, 'ExportErtBoxGrid') === 'YES'
      exchangeMode =
        getMandatoryTextValue(updateGRFElement, 'ExchangeMode') === 'AUTO'
      fileFormat = getMandatoryTextValue(updateGRFElement, 'FileFormat')
      extrapolationMethod = getMandatoryTextValue(
        updateGRFElement,
        'ExtrapolationMethod',
      )
      exportCheck =
        getMandatoryTextValue(fmuSettingsElement, 'ExportConfigFiles') === 'YES'
      onlyResidual =
        getMandatoryTextValue(fmuSettingsElement, 'UseResidualFields') === 'YES'
      useAPSConfigFile =
        getMandatoryTextValue(fmuSettingsElement, 'UseNonStandardFMU') === 'YES'
      break
    case "NOFIELD":
      exportCheck =
        getMandatoryTextValue(fmuSettingsElement, 'ExportConfigFiles') === 'YES'
      useAPSConfigFile =
        getMandatoryTextValue(fmuSettingsElement, 'UseNonStandardFMU') === 'YES'
      break
  }

  const runSettingsElement = getMandatoryNodeValue(
    jobSettingsElement,
    'RunSettings',
  )
  const maxFractionNotNormalised = getMandatoryNumericValue(
    runSettingsElement,
    'MaxFractionNotNormalised',
  )
  const toleranceLimitProbability = getMandatoryNumericValue(
    runSettingsElement,
    'ToleranceLimitProbability',
  )
  const transformationSettings = getMandatoryNumericValue(
    jobSettingsElement,
    'TransformationSettings',
    isTransformType,
  )
  const logSetting = getMandatoryNumericValue(jobSettingsElement, 'LogSetting', isDebugLevel)

  const settings: JobSettingsParam = {
    runFmuWorkflows: fmuMode === 'FIELDS', // might have to wrap !! around paranthesis to evaluate as false if fmuMode is undefined/null
    onlyUpdateFromFmu: fmuMode === 'NOFIELDS',
    simulationGrid: fmuMode === 'FIELDS' && ertBoxGrid ? ertBoxGrid : 'ERTBOX',
    importFields: fmuMode === 'FIELDS' ? exchangeMode : false,
    fieldFileFormat: (fmuMode === 'FIELDS' ? fileFormat : 'roff') as FieldFormats,
    customTrendExtrapolationMethod:
      fmuMode === 'FIELDS' ? extrapolationMethod : 'mean',
    exportFmuConfigFiles:
      fmuMode === 'FIELDS' || fmuMode === 'NOFIELDS' ? exportCheck : false,
    onlyUpdateResidualFields: fmuMode === 'FIELDS' ? onlyResidual : false,
    useNonStandardFmu:
      fmuMode === 'FIELDS' || fmuMode === 'NOFIELDS' ? useAPSConfigFile : false,
    exportErtBoxGrid: fmuMode === 'FIELDS' ? exportErtBox : false,
    maxAllowedFractionOfValuesOutsideTolerance: maxFractionNotNormalised ?? 0.1,
    toleranceOfProbabilityNormalisation: toleranceLimitProbability ?? 0.2,
    transformType: transformationSettings ?? 0,
    debugLevel: logSetting ?? 0,
  }

  return settings
}

type Attributes<Type> = {
  [Property in keyof Type as `@_${string & Property}`]: Type[Property]
}

interface JobSettingsContent {
  FmuSettings: {
    FmuMode: 'OFF' | 'ON' | 'FIELDS' | 'NOFIELD' | 'NOFIELDS'
    UpdateGRF?: {
      ErtBoxGrid: string
      ExportErtBoxGrid: 'YES' | 'NO'
      ExchangeMode: 'AUTO' | 'SIMULATE'
      FileFormat: FieldFormats
      ExtrapolationMethod: TrendExtrapolationMethod
    }
    ExportConfigFiles?: 'YES' | 'NO'
    UseResidualFields?: 'YES' | 'NO'
    UseNonStandardFMU?: 'YES' | 'NO'
  }
  RunSettings: {
    MaxFractionNotNormalised: number
    ToleranceLimitProbability: number
  }
  TransformationSettings: 1 | 0,
  LogSetting: DebugLevel
}

type FaciesContent = {
  Code: number
} & Attributes<{
  name: string
}>

type MainFaciesTableContent = {
  Facies: FaciesContent[]
} & Attributes<{
  blockedWell: string
  blockedWellLog: string
}>

type MaybeFmuUpdatable = ({
  '#text': number
} & Attributes<{
  kw: string
}>) | number

interface LinearTrend {
  azimuth: MaybeFmuUpdatable
  directionStacking: 1 | -1
  stackAngle: MaybeFmuUpdatable
}

interface EllipticTrend  extends LinearTrend {
    curvature: MaybeFmuUpdatable
    origin_x: MaybeFmuUpdatable
    origin_y: MaybeFmuUpdatable
    origin_z_simbox: MaybeFmuUpdatable
    origintype: 'Relative' | 'Absolute'
}

interface EllipticConeTrend  extends EllipticTrend {
  migrationAngle: MaybeFmuUpdatable
  relativeSize: MaybeFmuUpdatable
}

interface HyperbolicTrend extends EllipticConeTrend {
}

interface RMSParameterTrend {
  TrendParamName: string
}

interface RMSTrendMapTrend {
  TrendMapName: string
  TrendMapZone: string
}

type ZoneModelGaussFieldContent = {
  Vario: ({
    MainRange: MaybeFmuUpdatable
    PerpRange: MaybeFmuUpdatable
    VertRange: MaybeFmuUpdatable
    AzimuthAngle: MaybeFmuUpdatable
    DipAngle: MaybeFmuUpdatable
    Power?: MaybeFmuUpdatable
  }) & Attributes<{
    name:
      | 'SPHERICAL'
      | 'EXPONENTIAL'
      | 'GAUSSIAN'
      | 'GENERAL_EXPONENTIAL'
      | 'MATERN32'
      | 'MATERN52'
      | 'MATERN72'
      | 'CONSTANT'
  }>
  Trend: {
    Linear3D: LinearTrend
  } | {
    Elliptic3D: EllipticTrend
  } | {
    EllipticCone3D: EllipticConeTrend
  } | {
    Hyperbolic3D: HyperbolicTrend
  } | {
    RMSParameter: RMSParameterTrend
  } | {
    RMSTrendMap: RMSTrendMapTrend
  }
  RelStdDev: MaybeFmuUpdatable
  SeedForPreview: number
} & Attributes<{
  name: string
}>

interface TruncationRuleContentBayfill {
  BackGroundModel: {
    AlphaFields: string
    // These are the (named) facies
    Floodplain: string
    Subbay: string
    WBF: string
    BHD: string
    Lagoon: string

    // These are the slant factors
    SF: MaybeFmuUpdatable
    YSF: MaybeFmuUpdatable
    SBHD: MaybeFmuUpdatable
  }
}

interface TruncationRuleOverlayModelGroupContent {
  AlphaField: ({
    TruncIntervalCenter: number
    ProbFrac: ProbabilityFraction
  } & Attributes<{
    name: string
  }>)[]
  BackGround: string | string[]
}

interface TruncationRuleContentOverlayModel {
  OverLayModel?: ({
    Group: TruncationRuleOverlayModelGroupContent[]
  } & Attributes<{
    nGFields: string
  }>)
}

interface TruncationRuleContentNonCubic extends TruncationRuleContentOverlayModel {
  // That is, non-cubic truncation rule
  BackGroundModel: {
    AlphaFields: string  // That is Gaussian Random Fields
    UseConstTruncParam: 1 | 0
    Facies: ({
      Angle: MaybeFmuUpdatable
      ProbFrac: number
    } & Attributes<{
      name: string
    }>)[]
  }
}

type ProbabilityFraction = {
  '#text': number
} & Attributes<{
  name: string
}>

type ProcessedProbabilityFraction = ProbabilityFraction & Attributes<{
  // These where added by the preprocessor
  order: string
  parentId: ID
}>

interface ProbabilityFractions {
  ProbFrac: ProcessedProbabilityFraction[]
}

interface TruncationRuleContentCubic extends TruncationRuleContentOverlayModel {
  BackGroundModel: {
    AlphaFields: string
    L1: ProbabilityFractions & {
      L2?: ProbabilityFractions & {
        L3?: ProbabilityFractions
      }
    } & Attributes<{
      direction: 'V' | 'H'
      // These where added by the preprocessor
      order: string
      id: ID
    }>
  } & Attributes<{
    nGFields: string
  }>
}

type ZoneModelContentItem = {
  UseConstProb: 1 | 0
  SimBoxThickness: number
  FaciesProbForModel: {
    Facies: ({
      ProbCube: number
    } & Attributes<{
      name: ProbabilityCube
    }>)[]
  }
  GaussField: ZoneModelGaussFieldContent[]
  TruncationRule: {
    Trunc3D_Bayfill: TruncationRuleContentBayfill
  } | {
    Trunc2D_Angle: TruncationRuleContentNonCubic
  } | {
    Trunc2D_Cubic: TruncationRuleContentCubic
  }
  GridLayout?: 'Proportional' | 'BaseConform' | 'TopConform'
} & Attributes<{
    number: string
    regionNumber: string
  }>

interface ZoneModelContent {
  Zone: ZoneModelContentItem[]
}

type APSModelContent = Attributes<{
  version: string
}> & {
  RMSProjectName: string
  RMSWorkflowName?: string
  GridModelName: string
  ZoneParamName: string
  RegionParamName?: string
  ResultFaciesParamName: string
  JobSettings?: JobSettingsContent
  MainFaciesTable: MainFaciesTableContent
  ZoneModels: ZoneModelContent
}


export interface ConvertedXMLContent {
  '?xml': Attributes<{
    version: string
  }>
  APSModel: APSModelContent
}



export const useModelFileLoaderStore = defineStore('model-file-loader', () => {
    /**
     * This is the entry point for loading a model file
     * @param json
     * @param fileName
     * @returns {Promise<void>}
     */
    async function populateGUI (
      json: string,
      fileName: string,
    ): Promise<void> {
      const apsModelContainer = (JSON.parse(json) as ConvertedXMLContent)['APSModel']
      if (!apsModelContainer)
        throw new APSError('The model is missing the keyword "APSModel"')

      const parameterNameModelStore = useParameterNameModelStore()
      parameterNameModelStore.select(fileName)

      const rootStore = useRootStore()
      rootStore.startLoading(`Loading the model file, "${fileName}"`)

      const actions: {
        action: (value: string) => Promise<void> | void
        property: keyof APSModelContent
        check: boolean
      }[] = [
        {
          action: useParameterNameWorkflowStore().select,
          property: 'RMSWorkflowName',
          check: true,
        },
        {
          // fetching the simbox can take a long time, so we do not doe it during the initial loading / parsing
          action: (name: string) => useGridModelStore().select(name, false),
          property: 'GridModelName',
          check: false,
        },
        {
          action: useParameterZoneStore().select,
          property: 'ZoneParamName',
          check: true,
        },
        {
          action: useParameterRegionStore().select,
          property: 'RegionParamName',
          check: true,
        },
        {
          action: useParameterRealizationStore().select,
          property: 'ResultFaciesParamName',
          check: true,
        },
      ]
      try {
        for (const { action, property, check } of actions) {
          if (check ? property in apsModelContainer : true) {
            await action((apsModelContainer[property] as string).trim())
          }
        }

        const apsModels = ensureArray(apsModelContainer.ZoneModels.Zone)

        await populateGlobalFaciesList(apsModelContainer['MainFaciesTable'])

        await populateJobSettings(apsModelContainer, json.includes('"@_kw":'))

        const localActions: ((apsModels: ZoneModelContentItem[]) => void | Promise<void>)[] = [
          populateGaussianRandomFields,
          populateFaciesProbabilities,
          populateTruncationRules,
          populateGridLayout,
          // Now we can select zones and regions on the left-hand side of the gui.
          selectZonesAndRegions,
        ]
        for (const action of localActions) {
          await action(apsModels)
        }
        const panelStore = usePanelStore()
        panelStore.open('settings', 'truncationRule')
        panelStore.open('preview', 'truncationRuleMap')
      } catch (reason) {
        displayMessage((reason as Error).message, 'error')
      } finally {
        rootStore.finishLoading()
      }
    }

    async function populateGridLayout (
      apsModels: ZoneModelContentItem[],
    ): Promise<void> {
      const { byCode, setConformity } = useZoneStore()

      for (const apsModel of apsModels) {
        const gridLayout = getTextValue(apsModel, 'GridLayout')
        if (gridLayout) {
          const zoneNumber = getZoneNumber(apsModel)
          const { zone } = byCode(zoneNumber)
          if (isValidConformity(gridLayout)) {
            setConformity(zone, gridLayout)
          } else {
            throw new Error(
              `<Zone number="${zoneNumber}"><GridLayout> contains an invalid value (${gridLayout}). It must be one of 'TopConform', 'BaseConform', 'Proportional'`
            )
          }
        }
      }
    }

    /**
     * Takes the main facies table from a file and compares it to the facies log loaded from the project
     * (based on selected blocked well). Facies both loaded from the project and present in the file are
     * selected. Any facies not present in the project is added and then selected.
     * This method returns a promise. In order to let it complete fully before moving on, call it with async - await
     * @param mainFaciesTableFromFile
     * @returns {Promise<void>}
     */
    async function populateGlobalFaciesList(
      mainFaciesTableFromFile: MainFaciesTableContent | null,
    ): Promise<void> {
      if (mainFaciesTableFromFile === null) throw new Error('<MainFaciesTable> is missing or empty from the model file')
      await useParameterBlockedWellStore()
        .select(mainFaciesTableFromFile["@_blockedWell"])
      await useParameterBlockedWellLogStore()
        .select(mainFaciesTableFromFile["@_blockedWellLog"])

      const { available: globalFacies, create } = useFaciesGlobalStore()
      for (const faciesContainer of mainFaciesTableFromFile.Facies) {
        // facies information from the file.
        const name = faciesContainer['@_name'].trim()
        const code = Number(faciesContainer.Code)
        if (!isNumber(code)) {
          throw new Error(`The global facies, '${name}' has an invalid number (${code})`)
        } else if (code < 0) {
          throw new APSError(`The global facies, '${name}' has a negative code (${code})`)
        }

        // corresponding facies from project
        const facies = globalFacies.find(
          (facies): boolean => facies.name === name && facies.code === code,
        )

        // logic for selecting / adding
        if (!facies) {
          create({ code, name })
        }
      }
    }

    /**
     * This is the part that selects zones and regions combinations present in the file.
     * @param zoneModelsFromFile
     */
    async function selectZonesAndRegions (
      zoneModelsFromFile: ZoneModelContentItem[],
    ): Promise<void> {
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
        const regionNumber = zoneModel['@_regionNumber']
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
      let zoneToSetAsCurrent: Zone | null = null
      let regionToSetAsCurrent: Region | null = null
      const zonesToSelect: Zone[] = []
      const regionsToSelect: Region[] = []

      const {
        available: availableZones,
        setCurrentId: setCurrentZoneId,
        select: selectZones,
        touch: touchZone,
      } = useZoneStore()
      const {
        setCurrentId: setCurrentRegionId,
        select: selectRegions,
        touch: touchRegion,
      } = useRegionStore()
      for (const zoneRegionsItem of zoneRegionsMap) {
        const zoneIdFromFile = zoneRegionsItem[0]
        let zoneFound = false
        for (const id in availableZones) {
          const zone = availableZones[id] as Zone
          if (zone.code === zoneIdFromFile) {
            zoneFound = true
            zonesToSelect.push(zone as Zone)
            if (!zoneToSetAsCurrent) {
              zoneToSetAsCurrent = zone
            }
            const regionsInZone = zoneRegionsItem[1]
            for (let i = 0; i < regionsInZone.length; i++) {
              const regionIdFromFile = regionsInZone[i]
              let regionFound = false
              for (const regionId in zone.regions) {
                const region = zone.regions[regionId] as Region
                if (region.code === regionIdFromFile) {
                  regionFound = true
                  if (!regionToSetAsCurrent) {
                    // This is the first region to be selected and will be marked as current region. In order for this to
                    // be visible/consistent, the parent zone must also be "current". Therefore we overwrite zoneToSetASCurrent
                    zoneToSetAsCurrent = zone
                    regionToSetAsCurrent = region
                  }
                  regionsToSelect.push(region as Region)
                  // no need to loop through the rest of the zones´ regions.
                  break
                }
              }
              if (!regionFound) {
                // The file specified a zone with a region that does not exist in the project
                // we should ideally not be able to get here, as long as the file has been instantiated as an APS model
                // using the python code
                throw new Error(
                  `The input file has at least one region (region ${regionIdFromFile} for zone ${zoneIdFromFile} ) not specified in the current project`,
                )
              }
            }
            break
          }
        }
        if (!zoneFound) {
          // The file specified a zone that does not exist in the project
          // we should ideally not be able to get here, as long as the file has been instantiated as an APS model
          // using the python code
          throw new Error(
            `The input file has at least one zone (zone ${zoneIdFromFile}) not specified in the current project`,
          )
        }
      }
      // if we get here, the data is ok, we have identified what to select and can make the selection
      setCurrentZoneId(zoneToSetAsCurrent!.id)
      selectZones(zonesToSelect)
      await Promise.all(
        zonesToSelect.map((zone) =>
          touchZone({ zone } as Parent)
        ),
      )
      if (regionToSetAsCurrent) {
        setCurrentRegionId(regionToSetAsCurrent.id)
        selectRegions(regionsToSelect)
        await Promise.all(
          regionsToSelect.map((region) =>
            touchRegion(region)
          ),
        )
      }
    }

    /**
     * This adds and sets up the gaussian random fields specified in the file.
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    function populateGaussianRandomFields (
      zoneModelsFromFile: ZoneModelContentItem[],
    ): void {
      const { add } = useGaussianRandomFieldStore()
      for (const zoneModel of zoneModelsFromFile) {
        const parent = getParent(zoneModel)

        for (const gaussFieldFromFile of zoneModel.GaussField) {
          add(
            new GaussianRandomField({
              name: getName(gaussFieldFromFile),
              variogram: getVariogram(gaussFieldFromFile),
              trend: getTrend(gaussFieldFromFile),
              crossSection: getCrossSection(parent),
              seed: 'SeedForPreview' in gaussFieldFromFile
                ? getNumericValue(gaussFieldFromFile, 'SeedForPreview')
                : null,
              ...parent,
            })
          )
        }
      }
    }

    /**
     * Sets the facies probability for facies in zone. If the file specifies probCubes, the method sets the
     * probability to 1/number of fields in order to have the truncation rule visible after load
     * Note:
     * This will have to be updated in order to set correct selection based on zone/region.
     * as it is now it just updates the facies over and over again for each zone/region combo
     *
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    async function populateFaciesProbabilities(
      zoneModelsFromFile: ZoneModelContentItem[],
    ): Promise<void> {
      const {
        add,
        setConstantProbability,
        averageProbabilityCubes,
      } = useFaciesStore()
      const { available: availableGlobalFacies } = useFaciesGlobalStore()
      for (const zoneModel of zoneModelsFromFile) {
        const useConstantProb = getBooleanValue(zoneModel, 'UseConstProb')
        const parent = getParent(zoneModel)
        for (const faciesModel of getMandatoryNodeValue(zoneModel, 'FaciesProbForModel').Facies) {
          const facies = add(
              availableGlobalFacies.find((obj): boolean => obj.name === getName(faciesModel)) as GlobalFacies,
              parent,
          )

          setConstantProbability(
            facies.parentId, !!useConstantProb
          )
          if (useConstantProb) {
            const probability = getNumericValue(faciesModel, 'ProbCube')
            if (probability === null) throw new Error(`<UseConstProb> is set, but <ProbCube> is empty for Facies(name='${facies.name}', code=${facies.code})`)
            facies.previewProbability = probability
          } else {
            const probabilityCube = getTextValue(faciesModel, 'ProbCube')
            if (probabilityCube === null) throw  new Error(`<ProbCube> is not set for Facies(name='${facies.name}', code=${facies.code})`)
            facies.probabilityCube = probabilityCube
          }
        }
        if (!useConstantProb) {
          await averageProbabilityCubes({
              zoneNumber: parent.zone.code,
              useRegions: !!parent.region,
              regionNumber: parent.region ? parent.region.code : undefined,
            })
        }
      }
    }

    /**
     * Sets up Truncation Rules and connects them to fields as specified in the model file.
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    async function populateTruncationRules(
      zoneModelsFromFile: ZoneModelContentItem[],
    ): Promise<void> {
      const { add } = useTruncationRuleStore()
      const { change: changePresetType } = useTruncationRulePresetStore()
      const { available: availableTruncationRuleTemplateTypes, } = useTruncationRuleTemplateTypeStore()
      for (const zoneModel of zoneModelsFromFile) {
        const parent = getParent(zoneModel)

        if ('TruncationRule' in zoneModel) {
          const truncationRuleContainer = getMandatoryNodeValue(
            zoneModel,
            'TruncationRule',
          )
          let type = ''
          let rule = null
          if ('Trunc3D_Bayfill' in truncationRuleContainer) {
            type = 'Bayfill'
            rule = makeBayfillTruncationRule(
              getMandatoryNodeValue(truncationRuleContainer, 'Trunc3D_Bayfill'),
              parent,
            )
          } else if ('Trunc2D_Angle' in truncationRuleContainer) {
            type = 'Non-Cubic'
            rule = makeNonCubicTruncationRule(
              getMandatoryNodeValue(truncationRuleContainer, 'Trunc2D_Angle'),
              parent,
            )
          } else {
            type = 'Cubic'
            rule = makeCubicTruncationRule(
              getMandatoryNodeValue(truncationRuleContainer, 'Trunc2D_Cubic'),
              parent,
            )
          }
          if (rule) {
            // now we should have everything needed to add the truncationRule.
            add(rule)
          }

          // Changing presents must be done after the truncation rule is added (the command above must run to completion)
          changePresetType(
             availableTruncationRuleTemplateTypes.find((item): boolean => item.name === type)!?.type,
            null
          )
        }
      }
    }

    async function populateJobSettings(
      apsModelContainer: APSModelContent,
      modelFileContainsFmuSettings: boolean,
    ): Promise<void> {
      const { options: fmuOptions } = useFmuOptionStore()
      const { options } = useOptionStore()
      const jobSettingsParam = jobSettings(apsModelContainer, modelFileContainsFmuSettings)
      fmuOptions.runFmuWorkflows = jobSettingsParam.runFmuWorkflows
      fmuOptions.onlyUpdateFromFmu = jobSettingsParam.onlyUpdateFromFmu
      // Update JobSettings window for the three cases:
      // Run APS facies update in AHM/ERT: runFmuWorkflows = True, onlyUpdateFromFmu = False
      // Only run uncertainty update:      runFmuWorkflows = False, onlyUpdateFromFmu = True
      // No FMU mode:                      runFmuWorkflows = False, onlyUpdateFromFmu = False
      // The last combination should not be used
      //where runFmuWorkflows = True and onlyUpdateFromFmu = True

      fmuOptions.simulationGrid = jobSettingsParam.simulationGrid
      fmuOptions.fieldFileFormat = jobSettingsParam.fieldFileFormat
      fmuOptions.customTrendExtrapolationMethod = jobSettingsParam.customTrendExtrapolationMethod
      fmuOptions.onlyUpdateResidualFields = jobSettingsParam.onlyUpdateResidualFields
      fmuOptions.useNonStandardFmu = jobSettingsParam.useNonStandardFmu
      fmuOptions.exportErtBoxGrid = jobSettingsParam.exportErtBoxGrid

      options.importFields = jobSettingsParam.importFields
      options.exportFmuConfigFiles = jobSettingsParam.exportFmuConfigFiles

      useParametersMaxFractionOfValuesOutsideToleranceStore()
        .setTolerance(jobSettingsParam.maxAllowedFractionOfValuesOutsideTolerance)
      useParametersToleranceOfProbabilityNormalisationStore()
        .setTolerance(jobSettingsParam.toleranceOfProbabilityNormalisation)
      useParameterTransformTypeStore()
        .select(jobSettingsParam.transformType)
      useParameterDebugLevelStore()
        .select(
        jobSettingsParam.debugLevel
      )
    }
  return {
      populateGUI,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useModelFileLoaderStore, import.meta.hot),
  )
}
