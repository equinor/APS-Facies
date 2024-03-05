import { getRelevant } from '@/stores/utils/helpers'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type TruncationRuleBase from '@/utils/domain/truncationRule/base'
import type {
  CubicPolygon,
  Facies,
  GaussianRandomField,
  OverlayPolygon,
  Parent,
  Polygon,
  Region,
  InstantiatedTruncationRule,
  Zone,
  Bayfill,
  Cubic,
  NonCubic,
} from '@/utils/domain'
import type Variogram from '@/utils/domain/gaussianRandomField/variogram'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import type { Identified } from '@/utils/domain/bases/interfaces'
import { hasParents } from '@/utils'
import { hasOwnProperty } from '@/utils/helpers'
import { getFaciesName } from '@/utils/queries'
import type { Optional } from '@/utils/typing'
import { useParameterNameProjectStore } from '@/stores/parameters/names/project'
import { useParameterNameWorkflowStore } from '@/stores/parameters/names/workflow'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterZoneStore } from '@/stores/parameters/zone'
import { useRegionStore } from '@/stores/regions'
import { useParameterRegionStore } from '@/stores/parameters/region'
import { useParameterRealizationStore } from '@/stores/parameters/realization'
import { useParameterTransformTypeStore } from '@/stores/parameters/transform-type'
import {
  useParametersMaxFractionOfValuesOutsideToleranceStore,
  useParametersToleranceOfProbabilityNormalisationStore,
} from '@/stores/parameters/tolerance'
import { useFmuOptionStore } from '@/stores/fmu/options'
import { useOptionStore } from '@/stores/options'
import { useParameterDebugLevelStore } from '@/stores/parameters/debug-level'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { useFaciesStore } from '@/stores/facies'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { useZoneStore } from '@/stores/zones'
import { useParameterGridSimulationBoxStore } from '@/stores/parameters/grid/simulation-box'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { type RootStoreSerialization, useStateSerialization } from '@/stores'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'
import { DEFAULT_CROSS_SECTION } from '@/config'
import type { CrossSectionType } from '@/utils/domain/gaussianRandomField/crossSection'

class APSExportError extends Error {
  public constructor(message: string) {
    super(message)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, APSExportError)
    }
    this.name = 'APSExportError'
  }
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
function createElement(
  doc: Document,
  elemName: string,
  elemValue?: Value | null,
  attributes?: null | { name: string; value: Value }[],
): HTMLElement {
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

function addPreview(doc: Document, parentElement: HTMLElement) {
  const { current: currentZone } = useZoneStore()
  const { current: currentRegion } = useRegionStore()
  const crossSectionStore = useGaussianRandomFieldCrossSectionStore()

  const parent: Parent | null = currentZone ? {
    zone: currentZone,
    region: currentRegion,
  } : null
  let crossSectionType = (DEFAULT_CROSS_SECTION.type as CrossSectionType)
  if (parent) {
    const type = crossSectionStore.byParent(parent)
    if (type) {
      crossSectionType = type.type
    }
  }
  parentElement.appendChild(createElement(doc, 'Preview', null, [
    {
      name: 'zoneNumber',
      value: currentZone ? currentZone.code.toString(10) : "0",
    },
    {
      name: 'regionNumber',
      value: currentRegion ? currentRegion.code.toString(10) : "0",
    },
    {
      name: 'crossSectionType',
      value: crossSectionType,
    },
    {
      name: 'crossSectionRelativePos',
      value: '0.5',  // This value is not editable from the GUI
    },
    {
      name: 'scale',
      value: '1', // This value is not editable from the GUI
    }
  ]))
}

function addRMSProjectName(doc: Document, parentElement: HTMLElement): void {
  const parameterNameProjectStore = useParameterNameProjectStore()
  const name = parameterNameProjectStore.selected ?? '[ UNKNOWN ]'
  parentElement.appendChild(createElement(doc, 'RMSProjectName', name))
}

function addRMSWorkflowName(doc: Document, parentElement: HTMLElement): void {
  const parameterNameWorkflowStore = useParameterNameWorkflowStore()
  const value = parameterNameWorkflowStore.selected
  if (value) {
    parentElement.appendChild(createElement(doc, 'RMSWorkflowName', value))
  }
}

function addGridModelName(doc: Document, parentElement: HTMLElement): void {
  const gridModelStore = useGridModelStore()
  const value = gridModelStore.current?.name
  if (value) {
    parentElement.appendChild(createElement(doc, 'GridModelName', value))
  } else {
    throw new APSExportError('No grid model is selected')
  }
}

function addZoneParamName(doc: Document, parentElement: HTMLElement): void {
  const parameterZoneStore = useParameterZoneStore()
  // Default zone parameter name is Zone.
  const value = parameterZoneStore.selected || 'Zone'
  if (value) {
    parentElement.appendChild(createElement(doc, 'ZoneParamName', value))
  } else {
    throw new APSExportError('No Zone parameter is selected')
  }
}

function addRegionParamName(doc: Document, parentElement: HTMLElement): void {
  const regionStore = useRegionStore()
  const parameterRegionStore = useParameterRegionStore()
  if (regionStore.use) {
    parentElement.appendChild(
      createElement(doc, 'RegionParamName', parameterRegionStore.selected),
    )
  }
}

function addResultFaciesParamName(
  doc: Document,
  parentElement: HTMLElement,
): void {
  const parameterRealizationStore = useParameterRealizationStore()
  const value = parameterRealizationStore.selected
  if (value) {
    parentElement.appendChild(
      createElement(doc, 'ResultFaciesParamName', value),
    )
  } else {
    throw new APSExportError('No result facies parameter is given')
  }
}

function addKeyword(
  doc: Document,
  keyword: string,
  value: Optional<string>,
  parentElement: HTMLElement,
  required: boolean = false,
): HTMLElement {
  if (required) {
    if (!value) throw new APSExportError('Missing value for keyword ' + keyword)
  }
  const element = createElement(doc, keyword, value)
  parentElement.appendChild(element)
  return element
}

function addJobSettings(doc: Document, parentElement: HTMLElement): void {
  const fmuOptionStore = useFmuOptionStore()
  const optionStore = useOptionStore()
  // Get the job settings
  const transformType = useParameterTransformTypeStore().level
  const probFrac =
    useParametersMaxFractionOfValuesOutsideToleranceStore().tolerance
  const probTol =
    useParametersToleranceOfProbabilityNormalisationStore().tolerance
  const logSetting = useParameterDebugLevelStore().level

  const onlyUpdateFromFmu = fmuOptionStore.options.onlyUpdateFromFmu
  const fmuUpdateFields = fmuOptionStore.options.runFmuWorkflows
  const fmuFileFormat = fmuOptionStore.options.fieldFileFormat
  const fmuGrid = String(fmuOptionStore.options.simulationGrid)
  const fmuOnlyUpdateResidualFields =
    fmuOptionStore.options.onlyUpdateResidualFields
  const useNonStandardFmu = fmuOptionStore.options.useNonStandardFmu
  const exportErtBoxGrid = fmuOptionStore.options.exportErtBoxGrid
  const fmuTrendExtrapolation =
    fmuOptionStore.options.customTrendExtrapolationMethod

  const exportFmuConfigFiles = optionStore.options.exportFmuConfigFiles
  const importFieldsFromFmu = optionStore.options.importFields

  const fmuMode = fmuUpdateFields
    ? 'FIELDS'
    : onlyUpdateFromFmu
    ? 'NOFIELDS'
    : 'OFF'
  const exchangeMode = importFieldsFromFmu ? 'AUTO' : 'SIMULATE'
  const exportConfigMode = exportFmuConfigFiles ? 'YES' : 'NO'
  const useResidualFields = fmuOnlyUpdateResidualFields ? 'YES' : 'NO'
  const useNonStandardFMUSettings = useNonStandardFmu ? 'YES' : 'NO'
  const exportErtBoxGridSettings = exportErtBoxGrid ? 'YES' : 'NO'

  // Create the JobSettings keyword for the xml file
  const jobSettingsElement = addKeyword(doc, 'JobSettings', null, parentElement)
  const fmuSettingsElement = addKeyword(
    doc,
    'FmuSettings',
    null,
    jobSettingsElement,
  )

  addKeyword(doc, 'FmuMode', fmuMode, fmuSettingsElement, true)
  if (fmuMode === 'FIELDS') {
    const updateGRFElement = addKeyword(
      doc,
      'UpdateGRF',
      null,
      fmuSettingsElement,
    )
    addKeyword(doc, 'ErtBoxGrid', fmuGrid, updateGRFElement, true)
    addKeyword(
      doc,
      'ExportErtBoxGrid',
      exportErtBoxGridSettings,
      updateGRFElement,
      true,
    )
    addKeyword(doc, 'ExchangeMode', exchangeMode, updateGRFElement, true)
    addKeyword(doc, 'FileFormat', fmuFileFormat, updateGRFElement, true)
    addKeyword(
      doc,
      'ExtrapolationMethod',
      fmuTrendExtrapolation,
      updateGRFElement,
      true,
    )
    addKeyword(
      doc,
      'UseResidualFields',
      useResidualFields,
      fmuSettingsElement,
      true,
    )
    addKeyword(
      doc,
      'UseNonStandardFMU',
      useNonStandardFMUSettings,
      fmuSettingsElement,
      true,
    )
  }
  if (fmuMode === 'FIELDS' || fmuMode === 'NOFIELDS') {
    addKeyword(
      doc,
      'ExportConfigFiles',
      exportConfigMode,
      fmuSettingsElement,
      true,
    )
  }

  const runSettingsElement = addKeyword(
    doc,
    'RunSettings',
    null,
    jobSettingsElement,
  )
  addKeyword(
    doc,
    'MaxFractionNotNormalised',
    String(probFrac),
    runSettingsElement,
    true,
  )
  addKeyword(
    doc,
    'ToleranceLimitProbability',
    String(probTol),
    runSettingsElement,
    true,
  )

  addKeyword(
    doc,
    'TransformationSettings',
    String(transformType),
    jobSettingsElement,
  )
  addKeyword(doc, 'LogSetting', String(logSetting), jobSettingsElement)
}

function addMainFaciesTable(doc: Document, parentElement: HTMLElement): void {
  // getting blockedWell and blockedWellLog
  const bwParam = useParameterBlockedWellStore().selected
  const bwLogParam = useParameterBlockedWellLogStore().selected
  const mainFaciesElement = createElement(doc, 'MainFaciesTable', null, [
    { name: 'blockedWell', value: bwParam || '' },
    { name: 'blockedWellLog', value: bwLogParam || '' },
  ])
  parentElement.appendChild(mainFaciesElement)
  // finding all available facies
  const faciesGlobalStore = useGlobalFaciesStore()
  const allFacies = faciesGlobalStore.available.sort((a, b) => a.code - b.code)
  allFacies.forEach((facies): void => {
    const faciesElem = createElement(doc, 'Facies', null, [
      { name: 'name', value: facies.name },
    ])
    mainFaciesElement.append(faciesElem)
    const codeElem = createElement(doc, 'Code', facies.code)
    faciesElem.append(codeElem)
  })
}

function addFaciesProb(
  doc: Document,
  parent: Parent,
  zoneElement: HTMLElement,
): void {
  const probModelElem = createElement(doc, 'FaciesProbForModel')
  zoneElement.append(probModelElem)

  const faciesStore = useFaciesStore()

  const relevantFacies = getRelevant(faciesStore.available as Facies[], parent)
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
    const faciesName = faciesStore.name(facies) as string // TODO: Do i need to do this?
    const probFaciesElem = createElement(doc, 'Facies', null, [
      { name: 'name', value: faciesName },
    ])
    probModelElem.append(probFaciesElem)

    const useConstantProb = faciesStore.constantProbability(parent)
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

function addVariogram(
  doc: Document,
  variogram: Variogram,
  baseKw: string,
  fieldElement: HTMLElement,
): void {
  const variogramElement = createElement(doc, 'Vario', null, [
    { name: 'name', value: variogram.type },
  ])

  variogramElement.append(
    createElement(
      doc,
      'MainRange',
      variogram.range.main.value,
      variogram.range.main.updatable
        ? [{ name: 'kw', value: baseKw + '_RESIDUAL_MAINRANGE' }]
        : null,
    ),
  )

  variogramElement.append(
    createElement(
      doc,
      'PerpRange',
      variogram.range.perpendicular.value,
      variogram.range.perpendicular.updatable
        ? [{ name: 'kw', value: baseKw + '_RESIDUAL_PERPRANGE' }]
        : null,
    ),
  )

  variogramElement.append(
    createElement(
      doc,
      'VertRange',
      variogram.range.vertical.value,
      variogram.range.vertical.updatable
        ? [{ name: 'kw', value: baseKw + '_RESIDUAL_VERTRANGE' }]
        : null,
    ),
  )

  variogramElement.append(
    createElement(
      doc,
      'AzimuthAngle',
      variogram.angle.azimuth.value,
      variogram.angle.azimuth.updatable
        ? [{ name: 'kw', value: baseKw + '_RESIDUAL_AZIMUTHANGLE' }]
        : null,
    ),
  )

  variogramElement.append(
    createElement(
      doc,
      'DipAngle',
      variogram.angle.dip.value,
      variogram.angle.dip.updatable
        ? [{ name: 'kw', value: baseKw + '_RESIDUAL_DIPANGLE' }]
        : null,
    ),
  )

  if (variogram.type === 'GENERAL_EXPONENTIAL') {
    variogramElement.append(
      createElement(
        doc,
        'Power',
        variogram.power.value,
        variogram.power.updatable
          ? [{ name: 'kw', value: baseKw + '_POWER' }]
          : null,
      ),
    )
  }

  fieldElement.append(variogramElement)
}

function addTrend(
  doc: Document,
  field: GaussianRandomField,
  parent: Parent,
  baseKw: string,
  fieldElement: HTMLElement,
): void {
  const trendElement = createElement(doc, 'Trend', null, null)
  fieldElement.append(trendElement)

  // mapping from trend type names used in the store to the ones to be used in the exported file.
  const trendTypeMap = new Map()
  trendTypeMap.set('RMS_PARAM', 'RMSParameter')
  trendTypeMap.set('RMS_TRENDMAP', 'RMSTrendMap')
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
  const rmsTrendMapName = field.trend.trendMapName
  const rmsTrendMapZone = field.trend.trendMapZone
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
    const trendParamName = createElement(
      doc,
      'TrendParamName',
      rmsTrendParam,
      null,
    )
    trendTypeElement.append(trendParamName)
  } else if (trendType === 'RMSTrendMap') {
    const trendMapName = createElement(
      doc,
      'TrendMapName',
      rmsTrendMapName,
      null,
    )
    trendTypeElement.append(trendMapName)
    const trendMapZone = createElement(
      doc,
      'TrendMapZone',
      rmsTrendMapZone,
      null,
    )
    trendTypeElement.append(trendMapZone)
  } else {
    // azimuth, directionStacking and stackAngle common to all trends except rms parameter

    // azimuth
    trendTypeElement.append(
      createElement(
        doc,
        'azimuth',
        azimuth.value,
        azimuth.updatable
          ? [{ name: 'kw', value: baseKw + '_TREND_AZIMUTH' }]
          : null,
      ),
    )

    // directionStacking
    if (!stackingDirection) {
      if (parent.region) {
        throw new APSExportError(
          `Missing Stacking direction for field ${field.name} in zone ${parent.zone.code}, region ${parent.region.code}`,
        )
      } else {
        throw new APSExportError(
          `Missing Stacking direction for field ${field.name} in zone ${parent.zone.code}`,
        )
      }
    }
    trendTypeElement.append(
      createElement(
        doc,
        'directionStacking',
        stackingDirection === 'PROGRADING' ? 1 : -1,
        null,
      ),
    )

    // stackAngle
    trendTypeElement.append(
      createElement(
        doc,
        'stackAngle',
        stackAngle.value,
        stackAngle.updatable
          ? [{ name: 'kw', value: baseKw + '_TREND_STACKANGLE' }]
          : null,
      ),
    )

    if (trendType === 'EllipticCone3D' || trendType === 'Hyperbolic3D') {
      // migrationAngle is specific to EllipticCone3D and Hyperbolic3D
      trendTypeElement.append(
        createElement(
          doc,
          'migrationAngle',
          migrationAngle.value,
          migrationAngle.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_MIGRATIONANGLE' }]
            : null,
        ),
      )
    }

    if (trendType !== 'Linear3D') {
      // curvature is a child of everything not Linear3D (and RMSParameter of course)
      trendTypeElement.append(
        createElement(
          doc,
          'curvature',
          curvature.value,
          curvature.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_CURVATURE' }]
            : null,
        ),
      )
    }

    if (trendType === 'EllipticCone3D') {
      // relativeSize is specific to EllipticCone3D
      trendTypeElement.append(
        createElement(
          doc,
          'relativeSize',
          relativeSize.value,
          relativeSize.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_RELATIVESIZE' }]
            : null,
        ),
      )
    }

    if (trendType !== 'Linear3D') {
      // Origin information applies to everything not Linear3D

      // origin, x direction,
      trendTypeElement.append(
        createElement(
          doc,
          'origin_x',
          originX.value,
          originX.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_X' }]
            : null,
        ),
      )

      // origin, y direction,
      trendTypeElement.append(
        createElement(
          doc,
          'origin_y',
          originY.value,
          originY.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Y' }]
            : null,
        ),
      )

      // origin, z direction (simulation box)
      trendTypeElement.append(
        createElement(
          doc,
          'origin_z_simbox',
          originZ.value,
          originZ.updatable
            ? [{ name: 'kw', value: baseKw + '_TREND_ORIGIN_Z_SIMBOX' }]
            : null,
        ),
      )

      // origin type
      trendTypeElement.append(createElement(doc, 'origintype', originType))
    }
  }
}

function addGaussianRandomField(
  doc: Document,
  field: GaussianRandomField,
  parent: Parent,
  zoneElement: HTMLElement,
): void {
  const fieldElement = createElement(doc, 'GaussField', null, [
    { name: 'name', value: field.name },
  ])
  zoneElement.append(fieldElement)
  // generating a base string to be used in kw attributes for this field.
  const regionCode = parent.region ? parent.region.code : 0
  const baseKw = `APS_${parent.zone.code}_${regionCode}_GF_${field.name}`
  // attach vario, trend, relative standard deviation and seed to field:
  addVariogram(doc, field.variogram, baseKw, fieldElement)
  if (field.trend.use && field.trend.type !== 'NONE') {
    addTrend(doc, field, parent, baseKw, fieldElement)
    fieldElement.append(
      createElement(
        doc,
        'RelStdDev',
        field.trend.relativeStdDev.value,
        field.trend.relativeStdDev.updatable
          ? [{ name: 'kw', value: baseKw + '_TREND_RELSTDDEV' }]
          : null,
      ),
    )
  }
  fieldElement.append(createElement(doc, 'SeedForPreview', field.settings.seed))
}

function addGaussianRandomFields(
  doc: Document,
  parent: Parent,
  zoneElement: HTMLElement,
): void {
  const fieldStore = useGaussianRandomFieldStore()
  const relevantFields = getRelevant(fieldStore.available as GaussianRandomField[], parent)
    .sort((a, b): number =>
      a.name.localeCompare(b.name, undefined, { numeric: true }),
    )
  if (relevantFields.length < 2) {
    let message = ''
    if (parent.region) {
      message = `Zone ${parent.zone.code} / region ${parent.region.code}`
    } else {
      message = `Zone ${parent.zone.code}`
    }
    throw new APSExportError(
      message + ' has less than 2 Gaussian Random Fields',
    )
  } else {
    relevantFields.forEach((field) =>
      addGaussianRandomField(
        doc,
        field as GaussianRandomField,
        parent,
        zoneElement,
      ),
    )
  }
}

function getNumberOfFieldsForTruncRule(parent: Parent): number {
  const fieldStore = useGaussianRandomFieldStore()

  const relevantFields = getRelevant(fieldStore.available as GaussianRandomField[], parent)
  return relevantFields.length
}

function findFaciesNameForNamedPolygon(
  truncRule: Bayfill,
  polygonName: string,
): string {
  const polygonInRule = truncRule.polygons.find(
    (polygon): boolean => polygon.name === polygonName,
  )
  return polygonInRule && polygonInRule.facies ? polygonInRule.facies.name : ''
}

function getAlphaNames<
    T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends TruncationRuleBase<T, S, P>,
>(truncRule: RULE): string {
  const alphaFields = truncRule.backgroundFields
  return alphaFields.map((field): string => (field ? field.name : '')).join(' ')
}

function addTruncationRuleBayFill(
  doc: Document,
  parent: Parent,
  truncRule: Bayfill,
  truncRuleElem: HTMLElement,
): void {
  const numberOfFields = getNumberOfFieldsForTruncRule(parent)
  const bayFillElem = createElement(doc, 'Trunc3D_Bayfill', null, [
    { name: 'nGFields', value: numberOfFields },
  ])
  truncRuleElem.append(bayFillElem)

  const BackGroundModelElem = createElement(doc, 'BackGroundModel')
  bayFillElem.append(BackGroundModelElem)

  const alphaNames = getAlphaNames(truncRule)
  BackGroundModelElem.append(createElement(doc, 'AlphaFields', alphaNames))

  BackGroundModelElem.append(createElement(doc, 'UseConstTruncParam', 1)) // See issue 101 (https://git.equinor.com/APS/GUI/issues/101)

  // polygons
  BackGroundModelElem.append(
    createElement(
      doc,
      'Floodplain',
      findFaciesNameForNamedPolygon(truncRule, 'Floodplain'),
    ),
  )
  BackGroundModelElem.append(
    createElement(
      doc,
      'Subbay',
      findFaciesNameForNamedPolygon(truncRule, 'Subbay'),
    ),
  )
  BackGroundModelElem.append(
    createElement(
      doc,
      'WBF',
      findFaciesNameForNamedPolygon(truncRule, 'Wave influenced Bayfill'),
    ),
  )
  BackGroundModelElem.append(
    createElement(
      doc,
      'BHD',
      findFaciesNameForNamedPolygon(truncRule, 'Bayhead Delta'),
    ),
  )
  BackGroundModelElem.append(
    createElement(
      doc,
      'Lagoon',
      findFaciesNameForNamedPolygon(truncRule, 'Lagoon'),
    ),
  )

  // slant factors
  const baseKw = `APS_${parent.zone.code}_${
    parent.region ? parent.region.code : 0
  }_TRUNC_BAYFILL`

  truncRule.specification.polygons.forEach((setting): void => {
    BackGroundModelElem.append(
      createElement(
        doc,
        setting.name,
        setting.factor.value,
        setting.factor.updatable
          ? [{ name: 'kw', value: baseKw + `_${setting.name}` }]
          : null,
      ),
    )
  })
}

function addTruncationRuleOverlay<
  T extends Polygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P>,
>(
  doc: Document,
  parent: Parent,
  truncRule: RULE,
  truncRuleElem: HTMLElement,
  elementName: string,
  backgroundPolygonsHandler: (backGroundModelElem: HTMLElement) => void,
): void {
  const numberOfFields = getNumberOfFieldsForTruncRule(parent)
  const truncElement = createElement(doc, elementName, null, [
    { name: 'nGFields', value: numberOfFields },
  ])
  truncRuleElem.append(truncElement)

  const backGroundModelElem = createElement(doc, 'BackGroundModel')
  truncElement.append(backGroundModelElem)

  const alphaNames = getAlphaNames(truncRule)
  backGroundModelElem.append(createElement(doc, 'AlphaFields', alphaNames))
  // The background polygons
  backgroundPolygonsHandler(backGroundModelElem)

  const overlayGroups: Identified<OverlayPolygon[]> =
    truncRule.overlayPolygons.reduce((obj, polygon) => {
      const groupId = polygon.group.id
      if (!hasOwnProperty(obj, groupId)) obj[groupId] = []
      obj[groupId].push(polygon)
      return obj
    }, {} as Identified<OverlayPolygon[]>)
  if (Object.values(overlayGroups).length > 0 && truncRule.useOverlay) {
    const overLayModelElem = createElement(doc, 'OverLayModel')
    truncElement.append(overLayModelElem)

    Object.keys(overlayGroups).forEach((overlayGroup): void => {
      const groupElement = createElement(doc, 'Group')
      overLayModelElem.append(groupElement)

      overlayGroups[overlayGroup].forEach((polygon): void => {
        const alphaFieldElement = createElement(doc, 'AlphaField', null, [
          {
            name: 'name',
            value: polygon.field ? polygon.field.name : '',
          },
        ])
        groupElement.append(alphaFieldElement)

        alphaFieldElement.append(
          createElement(doc, 'TruncIntervalCenter', polygon.center as number),
        )

        alphaFieldElement.append(
          createElement(doc, 'ProbFrac', polygon.fraction, [
            {
              name: 'name',
              value: getFaciesName(polygon),
            },
          ]),
        )
      })
      const faciesGroupStore = useFaciesGroupStore()

      const group = faciesGroupStore.identifiedAvailable[overlayGroup]
      group.facies.forEach(({ name }) =>
        groupElement.append(createElement(doc, 'BackGround', name)),
      )
    })
  }
}

function addTruncationRuleCubic(
  doc: Document,
  parent: Parent,
  truncRule: Cubic,
  truncRuleElem: HTMLElement,
): void {
  function handleBackgroundPolygons(backGroundModelElem: HTMLElement): void {
    function addFraction(element: HTMLElement, polygon: CubicPolygon): void {
      element.append(
        createElement(doc, 'ProbFrac', polygon.fraction, [
          { name: 'name', value: getFaciesName(polygon) },
        ]),
      )
    }
    function addPolygon(element: HTMLElement, polygon: CubicPolygon): void {
      if (polygon.children.length > 0) {
        const attributes = !polygon.parent
          ? [{ name: 'direction', value: truncRule.direction.specification }]
          : null
        const child = createElement(
          doc,
          `L${polygon.atLevel + 1}`,
          null,
          attributes,
        )
        element.append(child)
        polygon.children.toSorted((a, b) => a.order - b.order).forEach((polygon): void => {
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
    doc,
    parent,
    truncRule,
    truncRuleElem,
    'Trunc2D_Cubic',
    handleBackgroundPolygons,
  )
}

function addTruncationRuleNonCubic(
  doc: Document,
  parent: Parent,
  truncRule: NonCubic,
  truncRuleElem: HTMLElement,
): void {
  function handleBackgroundPolygons(backGroundModelElem: HTMLElement): void {
    backGroundModelElem.append(createElement(doc, 'UseConstTruncParam', 1)) // See issue 101 (https://git.equinor.com/APS/GUI/issues/101)
    truncRule.backgroundPolygons.forEach((polygon): void => {
      // facies Element
      const faciesName = getFaciesName(polygon)
      const faciesElem = createElement(doc, 'Facies', null, [
        { name: 'name', value: faciesName },
      ])
      backGroundModelElem.append(faciesElem)
      // angle element
      const kwValue = `APS_${parent.zone.code}_${
        parent.region ? parent.region.code : 0
      }_TRUNC_NONCUBIC_POLYNUMBER_${polygon.order + 1}_ANGLE`
      faciesElem.append(
        createElement(
          doc,
          'Angle',
          polygon.angle.value,
          polygon.angle.updatable ? [{ name: 'kw', value: kwValue }] : null,
        ),
      )
      // ProbFrac element
      faciesElem.append(createElement(doc, 'ProbFrac', polygon.fraction))
    })
  }
  addTruncationRuleOverlay(
    doc,
    parent,
    truncRule,
    truncRuleElem,
    'Trunc2D_Angle',
    handleBackgroundPolygons,
  )
}

function addTruncationRule(
  doc: Document,
  parent: Parent,
  zoneElement: HTMLElement,
): void {
  const truncRuleElem = createElement(doc, 'TruncationRule')
  zoneElement.append(truncRuleElem)

  const truncationRuleStore = useTruncationRuleStore()
  const truncRule = (truncationRuleStore.available as InstantiatedTruncationRule[])
    .find(rule => hasParents(rule, parent.zone, parent.region))
  if (!truncRule) {
    let errMessage = `No truncation rule specified for zone ${parent.zone.code}`
    if (parent.region) {
      errMessage = errMessage + ` , region ${parent.region.code}`
    }
    throw new APSExportError(errMessage)
  }
  if (truncRule.type === 'bayfill') {
    addTruncationRuleBayFill(doc, parent, truncRule, truncRuleElem)
  }
  else if (truncRule.type === 'non-cubic') {
    addTruncationRuleNonCubic(doc, parent, truncRule, truncRuleElem)
  }
  else if (truncRule.type === 'cubic') {
    addTruncationRuleCubic(doc, parent, truncRule, truncRuleElem)
  }
  else {
    console.error('unknown truncation rule', truncRule)
    throw new APSExportError(`Unknown truncation rule type for Zone: ${parent.zone}, Region: ${parent.region}`)
  }
}

function addZoneModel(
  doc: Document,
  parent: Parent,
  zoneModelsElement: HTMLElement,
): void {
  const zoneRegionAttributes = []
  zoneRegionAttributes.push({ name: 'number', value: parent.zone.code })
  if (parent.region) {
    zoneRegionAttributes.push({
      name: 'regionNumber',
      value: parent.region.code,
    })
  }
  const zoneElement = createElement(doc, 'Zone', null, zoneRegionAttributes)
  zoneModelsElement.append(zoneElement)

  const zoneStore = useZoneStore()
  const { zone } = zoneStore.byCode(parent.zone.code)
  if (zone.conformity) {
    zoneElement.append(createElement(doc, 'GridLayout', zone.conformity))
  }

  const faciesStore = useFaciesStore()
  const useConstantProbability = faciesStore.constantProbability(parent) ? 1 : 0
  zoneElement.append(createElement(doc, 'UseConstProb', useConstantProbability))

  const simBoxStore = useParameterGridSimulationBoxStore()
  const simboxHeight = simBoxStore.size.z
  let zValue: number

  if (simboxHeight === null) {
    zValue = 0
  } else if (typeof simboxHeight === 'object') {
    zValue = simboxHeight[zone.code]
  } else /*if (typeof  simboxHeight === 'number') */{
    // Assuming it is a number
    zValue = simboxHeight
  }
  zoneElement.append(
    createElement(
      doc,
      'SimBoxThickness',
      zValue,
    ),
  )

  addFaciesProb(doc, parent, zoneElement)

  addGaussianRandomFields(doc, parent, zoneElement)

  addTruncationRule(doc, parent, zoneElement)
}

function addZoneModels(doc: Document, parentElement: HTMLElement): void {
  const zoneModelsElem = createElement(doc, 'ZoneModels', null, null)
  parentElement.appendChild(zoneModelsElem)

  const zoneStore = useZoneStore()
  const selectedZones = zoneStore.available
    .filter(
      (zone): boolean =>
        zone.selected === true || zone.selected === 'intermediate',
    )
    .sort((z1, z2): number => z1.code - z2.code)
  if (selectedZones.length === 0) {
    throw new APSExportError('No zones/regions selected')
  }
  const regionStore = useRegionStore()
  const parameterRegionStore = useParameterRegionStore()
  selectedZones.forEach((zone) => {
    const useRegions = regionStore.use && !!parameterRegionStore.selected
    if (!useRegions) {
      addZoneModel(doc, { zone: zone as Zone, region: null }, zoneModelsElem)
    } else {
      const selectedRegions = Object.values(zone.regions)
        .filter((region): boolean => !!region.selected)
        .sort((r1, r2): number => r1.code - r2.code)
      selectedRegions.forEach((region): void => {
        addZoneModel(
          doc,
          { zone: zone as Zone, region: region as Region },
          zoneModelsElem,
        )
      })
    }
  })
}

function addContent(doc: Document, rootElem: HTMLElement, includeAuxiliaryData: boolean): void {
  if (includeAuxiliaryData) {
    addPreview(doc, rootElem)
  }
  addRMSProjectName(doc, rootElem)
  addRMSWorkflowName(doc, rootElem)
  addGridModelName(doc, rootElem)
  addZoneParamName(doc, rootElem)
  addRegionParamName(doc, rootElem)
  addResultFaciesParamName(doc, rootElem)
  addJobSettings(doc, rootElem)
  addMainFaciesTable(doc, rootElem)
  addZoneModels(doc, rootElem)
}

export function createModel(includeAuxiliaryData = false): string {
  const doc = document.implementation.createDocument('', '', null)
  const rootElem = createElement(doc, 'APSModel', null, [
    { name: 'version', value: '1.1' },
  ])
  doc.appendChild(rootElem)
  addContent(doc, rootElem, includeAuxiliaryData)
  const serializer = new XMLSerializer()
  return serializer.serializeToString(doc)
}

interface Job extends RootStoreSerialization {
  model: Optional<string>
  errorMessage: string | null
}
export function dumpState(): Job {
  let model = null
  let errorMessage: string | null = null
  try {
    model = btoa(createModel())
  } catch (e) {
    errorMessage = (e as Error)?.message
  }
  const state = useStateSerialization()
  return {
    ...state,
    model,
    errorMessage,
  }
}
