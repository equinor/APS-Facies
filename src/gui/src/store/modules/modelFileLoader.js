import { resolve } from '@/utils'
import { Variogram, Trend, GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import {
  Bayfill,
  BayfillPolygon,
  NonCubic,
  NonCubicPolygon,
  Cubic,
  CubicPolygon,
  OverlayPolygon,
} from '@/utils/domain'
import FmuUpdatableValue from '@/utils/domain/bases/fmuUpdatable'

const ensureArray = (value) => {
  if (Array.isArray(value)) {
    return value
  } else {
    const returnValue = []
    returnValue.push(value)
    return returnValue
  }
}

const getNodeValue = (container, prop) => {
  let value = resolve(prop, container)
  if (typeof value === 'undefined') return null
  if (value._text) {
    value = value._text.trim()
  }
  return value
}

const getOriginType = (elem) => {
  return elem && elem._text
    ? elem._text.trim().replace(/'/g, '').toUpperCase()
    : null
}

const isFMUUpdatable = (elem) => {
  return !!(elem && elem._attributes && elem._attributes.kw)
}

const getNumericValue = (elem) => {
  if (elem && elem._text) {
    return Number(elem._text.trim())
  }
  return null
}

const getTextValue = (elem) => {
  if (elem && elem._text) {
    return elem._text.trim()
  }
  return null
}

const getBooleanValue = (elem) => {
  if (elem && elem._text) {
    return Boolean(Number(elem._text.trim()))
  }
  return null
}

const getStackingDirection = (elem) => {
  if (elem && elem._text) {
    if (elem._text.trim() === '1') {
      return 'PROGRADING'
    }
    if (elem._text.trim() === '-1') {
      return 'RETROGRADING'
    }
  }
  return null
}

const handleError = (reason) => {
  alert(reason)
}

function getParent ({ rootState }, zoneModel) {
  const zone = Object.values(rootState.zones.available).find(zone => zone.code === parseInt(zoneModel._attributes.number))
  const region = zoneModel._attributes.regionNumber
    ? Object.values(zone.regions)
      .find(region => region.code === parseInt(zoneModel._attributes.regionNumber))
    : null
  return {
    zone,
    region,
  }
}

function getFacies ({ rootState }, name, parent) {
  return Object.values(rootState.facies.available)
    .filter(facies => facies.isChildOf(parent))
    .find(facies => facies.name === name)
}

function getBackgroundFacies ({ rootState }, container, parent) {
  const over = ensureArray(container.BackGround)

  return over.map(el => getFacies({ rootState }, getTextValue(el), parent))
}

function getFaciesFromBayfill ({ rootState }, container, item, parent) {
  const mappig = {
    'Bayhead Delta': 'BHD',
    'Wave influenced Bayfill': 'WBF',
  }
  if (item in mappig) item = mappig[`${item}`]
  const name = getTextValue(container.BackGroundModel[item])
  return getFacies({ rootState }, name, parent)
}

function getSlantFactor (container, item) {
  const mapping = {
    'Floodplain': 'SF',
    'Subbay': 'YSF',
    'Bayhead Delta': 'SBHD',
  }
  const element = container.BackGroundModel
  return item in mapping
    ? new FmuUpdatableValue({
      value: getNumericValue(element[mapping[`${item}`]]),
      updatable: isFMUUpdatable(element[mapping[`${item}`]])
    })
    : null
}

function getAlphaField ({ rootState }, name, parent) {
  return Object.values(rootState.gaussianRandomFields.fields)
    .filter(field => field.isChildOf(parent))
    .find(field => field.name === name)
}

function getAlphaFields ({ rootState }, container, parent) {
  const alphafields = getTextValue(container.BackGroundModel.AlphaFields)
  return alphafields.split(' ').map(name => getAlphaField({ rootState }, name, parent))
}

function makeBayfillTruncationRule ({ rootState }, container, parent) {
  const names = [
    'Floodplain',
    'Subbay',
    'Wave influenced Bayfill',
    'Bayhead Delta',
    'Lagoon',
  ]
  const polygons = names.map((name, index) => {
    return new BayfillPolygon({
      name,
      facies: getFaciesFromBayfill({ rootState }, container, name, parent),
      slantFactor: getSlantFactor(container, name),
      order: index + 1,
    })
  })

  const backgroundFields = getAlphaFields({ rootState }, container, parent)

  return new Bayfill({
    name: 'Imported',
    polygons,
    backgroundFields,
    parent,
  })
}

function getOverlayPolygon ({ rootState }, backgroundFacies, container, order, parent) {
  return new OverlayPolygon({
    group: backgroundFacies,
    center: getNumericValue(container.TruncIntervalCenter),
    field: getAlphaField({ rootState }, container._attributes.name, parent),
    fraction: getNumericValue(container.ProbFrac),
    facies: getFacies({ rootState }, container.ProbFrac._attributes.name, parent),
    order,
  })
}

async function getOverlayPolygons ({ rootState, dispatch }, group, parent, offset = 0) {
  const backgroundFacies = await dispatch('facies/groups/get', {
    facies: getBackgroundFacies({ rootState }, group, parent),
    parent,
  }, { root: true })
  const _getOverlayPolygon = (el, index = 0) => getOverlayPolygon({ rootState }, backgroundFacies, el, offset + index + 1, parent)
  const polygons = ensureArray(group.AlphaField)
  return polygons.map(_getOverlayPolygon)
}

async function makeOverlayPolygons ({ dispatch, rootState }, container, parent, offset = 0) {
  const overlayPolygons = []
  if (container.OverLayModel) {
    const groups = ensureArray(container.OverLayModel.Group)
    for (const group of groups) {
      const polygons = await getOverlayPolygons({ dispatch, rootState }, group, parent, overlayPolygons.length + offset)
      overlayPolygons.push(...polygons)
    }
  }
  return overlayPolygons
}

async function makeOverlayTruncationRule ({ rootState, dispatch }, container, parent, makeBackgroundPolygons, _class, extra = {}) {
  const backgroundFields = getAlphaFields({ rootState }, container, parent)
  const backgroundPolygons = makeBackgroundPolygons(container.BackGroundModel)

  const overlayPolygons = await makeOverlayPolygons({ dispatch, rootState }, container, parent, backgroundPolygons.length)
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

async function makeNonCubicTruncationRule ({ rootState, dispatch }, container, parent) {
  function makeNonCubicBackgroundFacies (container) {
    return container.Facies.map((element, index) => new NonCubicPolygon({
      angle: getNumericValue(element.Angle),
      fraction: getNumericValue(element.ProbFrac),
      facies: getFacies({ rootState }, element._attributes.name, parent),
      order: index + 1,
    }))
  }
  /* eslint-disable-next-line no-return-await */
  return await makeOverlayTruncationRule(
    { rootState, dispatch },
    container,
    parent,
    makeNonCubicBackgroundFacies,
    NonCubic,
  )
}

function ensureRoot (root, polygons) {
  if (!root) {
    root = new CubicPolygon({ parent: root, order: -1 })
    polygons.push(root)
  }
  return root
}

async function makeCubicTruncationRule ({ rootState, dispatch }, container, parent) {
  function getPolygon (element, order, root, parent) {
    return new CubicPolygon({
      parent: root,
      fraction: getNumericValue(element),
      facies: getFacies({ rootState }, element._attributes.name, parent),
      order,
    })
  }
  function getChildren (container, root) {
    const polygons = []
    let order = 1

    if (!root && container.L1) container = container.L1
    if (root) polygons.push(root)

    if (!container) return polygons
    else if (Array.isArray(container)) {
      container.forEach(element => {
        polygons.push(...getChildren(element, new CubicPolygon({ parent: root, order })))
        order += 1
      })
    } else {
      for (const key of Object.keys(container)) {
        if (key === 'ProbFrac' && container.ProbFrac) {
          if (Array.isArray(container.ProbFrac)) {
            root = ensureRoot(root, polygons)
            container.ProbFrac.forEach(element => {
              polygons.push(getPolygon(element, order, root, parent))
              order += 1
            })
          } else {
            polygons.push(getPolygon(container.ProbFrac, order, root, parent))
            order += 1
          }
        } else if (/L[0-9]+/.exec(key)) {
          polygons.push(...getChildren(container[`${key}`], new CubicPolygon({ parent: root, order })))
          order += 1
        }
      }
    }
    return polygons
  }

  /* eslint-disable-next-line no-return-await */
  return await makeOverlayTruncationRule(
    { rootState, dispatch },
    container,
    parent,
    container => getChildren(container, null),
    Cubic,
    {
      direction: container.BackGroundModel.L1._attributes.direction,
    }
  )
}

function getTrend (gaussFieldFromFile) {
  if (!gaussFieldFromFile.Trend) return null

  let type = null
  let trendContainer = null
  if (gaussFieldFromFile.Trend.Linear3D) {
    type = 'LINEAR'
    trendContainer = gaussFieldFromFile.Trend.Linear3D
  } else if (gaussFieldFromFile.Trend.Elliptic3D) {
    type = 'ELLIPTIC'
    trendContainer = gaussFieldFromFile.Trend.Elliptic3D
  } else if (gaussFieldFromFile.Trend.EllipticCone3D) {
    type = 'ELLIPTIC_CONE'
    trendContainer = gaussFieldFromFile.Trend.EllipticCone3D
  } else if (gaussFieldFromFile.Trend.Hyperbolic3D) {
    type = 'HYPERBOLIC'
    trendContainer = gaussFieldFromFile.Trend.Hyperbolic3D
  } else if (gaussFieldFromFile.Trend.RMSParameter) {
    type = 'RMS_PARAM'
    trendContainer = gaussFieldFromFile.Trend.RMSParameter
  }

  return new Trend({
    use: true,
    type: type,
    azimuth: getNumericValue(trendContainer.azimuth),
    azimuthUpdatable: isFMUUpdatable(trendContainer.azimuth),
    stackAngle: getNumericValue(trendContainer.stackAngle),
    stackAngleUpdatable: isFMUUpdatable(trendContainer.stackAngle),
    migrationAngle: getNumericValue(trendContainer.migrationAngle),
    migrationAngleUpdatable: isFMUUpdatable(trendContainer.migrationAngle),
    stackingDirection: getStackingDirection(trendContainer.directionStacking),
    parameter: getTextValue(trendContainer.TrendParamName),
    curvature: getNumericValue(trendContainer.curvature),
    curvatureUpdatable: isFMUUpdatable(trendContainer.curvature),
    originX: getNumericValue(trendContainer.origin_x),
    originXUpdatable: isFMUUpdatable(trendContainer.origin_x),
    originY: getNumericValue(trendContainer.origin_y),
    originYUpdatable: isFMUUpdatable(trendContainer.origin_y),
    originZ: getNumericValue(trendContainer.origin_z_simbox),
    originZUpdatable: isFMUUpdatable(trendContainer.origin_z_simbox),
    originType: getOriginType(trendContainer.origintype),
    relativeSize: getNumericValue(trendContainer.relativeSize),
    relativeSizeUpdatable: isFMUUpdatable(trendContainer.relativeSize),
    relativeStdDev: getNumericValue(gaussFieldFromFile.RelStdDev),
    relativeStdDevUpdatable: isFMUUpdatable(gaussFieldFromFile.RelStdDev),
  })
}

function getVariogram (gaussFieldFromFile) {
  return new Variogram({
    type: gaussFieldFromFile.Vario._attributes.name.trim(),
    // Angles
    azimuth: getNumericValue(gaussFieldFromFile.Vario.AzimuthAngle),
    azimuthUpdatable: isFMUUpdatable(gaussFieldFromFile.Vario.AzimuthAngle),
    dip: getNumericValue(gaussFieldFromFile.Vario.DipAngle),
    dipUpdatable: isFMUUpdatable(gaussFieldFromFile.Vario.DipAngle),
    // Ranges
    main: getNumericValue(gaussFieldFromFile.Vario.MainRange),
    mainUpdatable: isFMUUpdatable(gaussFieldFromFile.Vario.MainRange),
    perpendicular: getNumericValue(gaussFieldFromFile.Vario.PerpRange),
    perpendicularUpdatable: isFMUUpdatable(gaussFieldFromFile.Vario.PerpRange),
    vertical: getNumericValue(gaussFieldFromFile.Vario.VertRange),
    verticalUpdatable: isFMUUpdatable(gaussFieldFromFile.Vario.VertRange),
    power: gaussFieldFromFile.Vario._attributes.name === 'GENERAL_EXPONENTIAL'
      ? getNumericValue(gaussFieldFromFile.Vario.Power)
      : null,
    powerUpdatable: gaussFieldFromFile.Vario._attributes.name === 'GENERAL_EXPONENTIAL'
      && isFMUUpdatable(gaussFieldFromFile.Vario.Power)
  })
}

async function getCrossSection ({ dispatch }, parent) {
  const crossSection = await dispatch('gaussianRandomFields/crossSections/fetch', parent, { root: true })
  return crossSection
}

export default {
  namespaced: true,

  state: {},

  modules: {},

  actions: {

    /**
     * This is the entry point for loading a model file
     * @param dispatch
     * @param json
     * @param fileName
     * @returns {Promise<void>}
     */
    populateGUI: async ({ dispatch, commit }, { json, fileName }) => {
      const apsModelContainer = JSON.parse(json).APSModel

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
          if (check ? apsModelContainer[`${property}`] : true) {
            await dispatch(action, getNodeValue(apsModelContainer, property), { root: true })
          }
        }

        const apsModels = ensureArray(apsModelContainer.ZoneModels.Zone)

        await dispatch('populateGlobalFaciesList', apsModelContainer.MainFaciesTable)

        const localActions = [
          'populateGaussianRandomFields',
          'populateFaciesProbabilities',
          'populateTruncationRules',
          // Now we can select zones and regions on the left hand side of the gui.
          'selectZonesAndRegions',
        ]
        for (const action of localActions) {
          await dispatch(action, apsModels)
        }
      } catch (reason) {
        handleError(reason)
      } finally {
        commit('LOADING', { loading: false }, { root: true })
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
    populateGlobalFaciesList: async ({ dispatch, rootState }, mainFaciesTableFromFile) => {
      await dispatch('parameters/blockedWell/select', mainFaciesTableFromFile._attributes.blockedWell, { root: true })
      await dispatch('parameters/blockedWellLog/select', mainFaciesTableFromFile._attributes.blockedWellLog, { root: true })

      for (const faciesItemFromFile of mainFaciesTableFromFile.Facies) {
        // facies information from the file.
        const name = faciesItemFromFile._attributes.name.trim()
        const code = parseInt(faciesItemFromFile.Code._text.trim())

        // corresponding facies from project
        const facies = Object.values(rootState.facies.global.available)
          .find(facies => facies.name === name && facies.code === code)

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
    selectZonesAndRegions: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      // synthesizing zones and region info: Zones and regions could be specified in weird ways. For instance we could
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
      zoneModelsFromFile.forEach(zoneModel => {
        const zoneNumber = parseInt(zoneModel._attributes.number, 10)
        const regionNumber = zoneModel._attributes.regionNumber
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
            let regionsInZone = zoneRegionsItem[1]
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
      if (regionToSetAsCurrent) {
        await dispatch('regions/current', regionToSetAsCurrent, { root: true })
        await dispatch('regions/select', regionsToSelect, { root: true })
      }
    },

    /**
     * This adds and sets up the gaussian random fields specified in the file.
     * @param dispatch
     * @param rootState
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateGaussianRandomFields: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      for (const zoneModel of zoneModelsFromFile) {
        const parent = getParent({ rootState }, zoneModel)

        for (const gaussFieldFromFile of zoneModel.GaussField) {
          await dispatch('gaussianRandomFields/addField',
            new GaussianRandomField({
              name: gaussFieldFromFile._attributes.name,
              variogram: getVariogram(gaussFieldFromFile),
              trend: getTrend(gaussFieldFromFile),
              crossSection: await getCrossSection({ dispatch }, parent),
              parent,
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
     * @param dispatch
     * @param rootState
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateFaciesProbabilities: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      for (const zoneModel of zoneModelsFromFile) {
        const useConstantProb = getBooleanValue(zoneModel.UseConstProb)
        const parent = getParent({ rootState }, zoneModel)
        // TODO: handle SimBoxThickness (must await implementation from Sindre on this?)
        for (const faciesModel of zoneModel.FaciesProbForModel.Facies) {
          const facies = await dispatch('facies/add', {
            facies: /* global */ Object.values(rootState.facies.global.available).find(obj => obj.name === faciesModel._attributes.name),
            parent,
          }, { root: true })
          await dispatch('facies/setConstantProbability', { parentId: facies.parentId, toggled: useConstantProb }, { root: true })
          if (useConstantProb) {
            await dispatch('facies/updateProbability', {
              facies,
              probability: getNumericValue(faciesModel.ProbCube)
            }, { root: true })
          } else {
            const probabilityCube = faciesModel.ProbCube._text.trim()
            await dispatch('facies/changeProbabilityCube', { facies, probabilityCube }, { root: true })
          }
        }
        if (!useConstantProb) {
          await dispatch('facies/averageProbabilityCubes', { zoneNumber: parent.zone.code, useRegions: !!parent.region, regionNumber: parent.region && parent.region.code }, { root: true })
        }
      }
    },

    /**
     * Sets up Truncation Rules and connects them to fields as specified in the model file.
     * @param dispatch
     * @param rootState
     * @param rootGetters
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateTruncationRules: async ({ dispatch, commit, rootState }, zoneModelsFromFile) => {
      for (const zoneModel of zoneModelsFromFile) {
        const zoneNumber = parseInt(zoneModel._attributes.number)
        let regionNumber = parseInt(zoneModel._attributes.regionNumber)
        if (isNaN(regionNumber)) regionNumber = null

        const zone = Object.values(rootState.zones.available)
          .find(zone => zone.code === zoneNumber)
        const regionsForZone = rootState.zones.available[`${zone.id}`].regions
        const region = Object.values(regionsForZone)
          .find(region => region.code === regionNumber) || null

        const parent = {
          zone,
          region,
        }
        if (zoneModel.TruncationRule) {
          let truncationRuleContainer = zoneModel.TruncationRule
          let type = ''
          let rule = null
          if (truncationRuleContainer.Trunc3D_Bayfill) {
            type = 'Bayfill'
            rule = makeBayfillTruncationRule({ rootState }, truncationRuleContainer.Trunc3D_Bayfill, parent)
          } else if (truncationRuleContainer.Trunc2D_Angle) {
            type = 'Non-Cubic'
            rule = await makeNonCubicTruncationRule({ dispatch, rootState }, truncationRuleContainer.Trunc2D_Angle, parent)
          } else {
            rule = await makeCubicTruncationRule({ dispatch, rootState }, truncationRuleContainer.Trunc2D_Cubic, parent)
            type = 'Cubic'
          }
          if (rule) {
            // now we should have everything needed to add the truncationRule.
            await dispatch('truncationRules/add', rule, { root: true })
          }

          type = Object.values(rootState.truncationRules.templates.types.available)
            .find(item => item.name === type)
          // Changing presents must be done after the truncation rule is added (the command above must run to completion)
          commit('truncationRules/CHANGE_TYPE', { type }, { root: true })
          commit('truncationRules/CHANGE_TEMPLATE', { template: { text: 'Imported' } }, { root: true })
        }
      }
    }

  },

  mutations: {},

  getters: {},
}
