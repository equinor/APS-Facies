import { resolve } from '@/utils'
import { Variogram, Trend, GaussianRandomField } from '@/utils/domain/gaussianRandomField'
import { Bayfill, BayfillPolygon } from '@/utils/domain'
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
  let value = resolve(prop, container.APSModel)
  if (value._text) {
    value = value._text.trim()
  }
  return value
}

const getOriginType = (elem) => {
  if (elem && elem._text) {
    const value = elem._text.trim().replace(/'/g, '').toUpperCase()
    return value
  }
  return null
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
  let region = null
  if (zoneModel._attributes.regionNumber) {
    region = Object.values(zone.regions)
      .find(region => region.code === parseInt(zoneModel._attributes.regionNumber))
  }
  return {
    zone,
    region,
  }
}

function getFacies ({ rootState }, parent, truncationRuleContainer, item) {
  const mappig = {
    'Bayhead Delta': 'BHD',
    'Wave influenced Bayfill': 'WBF',
  }
  if (item in mappig) item = mappig[item]
  const name = getTextValue(truncationRuleContainer.Trunc3D_Bayfill.BackGroundModel[item])
  return Object.values(rootState.facies.available)
    .filter(facies => facies.isChildOf(parent))
    .find(facies => facies.name === name)
}

function getSlantFactor (truncationRuleContainer, item) {
  const mapping = {
    'Floodplain': 'SF',
    'Subbay': 'YSF',
    'Bayhead Delta': 'SBHD',
  }
  const element = truncationRuleContainer.Trunc3D_Bayfill.BackGroundModel
  return item in mapping
    ? new FmuUpdatableValue({
      value: getNumericValue(element[mapping[item]]),
      updatable: isFMUUpdatable(element[mapping[item]])
    })
    : null
}

function makeBayfillTruncationRule (truncationRuleContainer, rootState, parent) {
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
      facies: getFacies({ rootState }, parent, truncationRuleContainer, name),
      slantFactor: getSlantFactor(truncationRuleContainer, name),
      order: index,
    })
  })

  const alphafields = getTextValue(truncationRuleContainer.Trunc3D_Bayfill.BackGroundModel.AlphaFields)
  const fields = alphafields.split(' ').map(name => {
    return Object.values(rootState.gaussianRandomFields.fields)
      .filter(field => field.isChildOf(parent))
      .find(field => field.name === name)
  })

  const rule = new Bayfill({
    name: '',
    polygons,
    backgroundFields: fields,
    parent,
  })
  return rule
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
    populateGUI: async ({ dispatch }, { json, fileName }) => {
      const apsModelContainer = JSON.parse(json)

      await dispatch('parameters/names/model/select', fileName, { root: true })

      // TODO introduce function (repeating code. Code smell?)
      const optionalRMSWorkFlowName = getNodeValue(apsModelContainer, 'RMSWorkflowName')
      // try {
      if (optionalRMSWorkFlowName) {
        await dispatch('parameters/names/workflow/select', optionalRMSWorkFlowName, { root: true })
      }

      await dispatch('gridModels/select', getNodeValue(apsModelContainer, 'GridModelName'), { root: true })

      if (apsModelContainer.APSModel.RegionParamName) {
        await dispatch(`parameters/zone/select`, getNodeValue(apsModelContainer, 'ZoneParamName'), { root: true })
      }

      if (apsModelContainer.APSModel.RegionParamName) {
        await dispatch(`parameters/region/select`, getNodeValue(apsModelContainer, 'RegionParamName'), { root: true })
      }

      if (apsModelContainer.APSModel.ResultFaciesParamName) {
        await dispatch('parameters/realization/select', getNodeValue(apsModelContainer, 'ResultFaciesParamName'), { root: true })
      }

      await dispatch('populateGlobalFaciesList', apsModelContainer.APSModel.MainFaciesTable)

      await dispatch('populateGaussianRandomFields', ensureArray(apsModelContainer.APSModel.ZoneModels.Zone))

      await dispatch('populateFaciesProbabilities', ensureArray(apsModelContainer.APSModel.ZoneModels.Zone))

      await dispatch('populateTruncationRules', ensureArray(apsModelContainer.APSModel.ZoneModels.Zone))

      // Now we can select zones and regions on the left hand side of the gui.
      await dispatch('selectZonesAndRegions', ensureArray(apsModelContainer.APSModel.ZoneModels.Zone))
      // } catch (reason) {
      //   handleError(reason)
      // }
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
      // syntezing zones and region info: Zones and regions could be specified in weird ways. For instance we could
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
     * This adds and sets up the gaussian randomfields specified in the file.
     * @param dispatch
     * @param rootState
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateGaussianRandomFields: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      zoneModelsFromFile.forEach(zoneModel => {
        const zoneNumber = parseInt(zoneModel._attributes.number)
        let regionNumber = parseInt(zoneModel._attributes.regionNumber)
        if (isNaN(regionNumber)) regionNumber = null

        // The corresponding zone and region number in the internal datastructures
        const zone = Object.values(rootState.zones.available)
          .find(zone => zone.code === zoneNumber)
        const regionsForZone = zone.regions
        const region = Object.values(regionsForZone)
          .find(region => region.code === regionNumber)

        zoneModel.GaussField.forEach(async gaussFieldFromFile => {
          let trend = null

          if (gaussFieldFromFile.Trend) {
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

            trend = new Trend({
              use: true,
              type: type,
              azimuth: getNumericValue(trendContainer.azimuth),
              azimuthUpdatable: isFMUUpdatable(trendContainer.azimuth),
              stackAngle: getNumericValue(trendContainer.stackAngle),
              stackAngleUpdatable: isFMUUpdatable(trendContainer.stackAngle),
              migrationAngle: getNumericValue(trendContainer.migrationAngle),
              migrationAngleUpdatable: isFMUUpdatable(trendContainer.migrationAngle),
              stackingDirection: getStackingDirection(trendContainer.directionStacking),
              // TODO. Load parameters
              parameter: null,
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
              relativeSizeUpdateble: isFMUUpdatable(trendContainer.relativeSize),
              relativeStdDev: getNumericValue(gaussFieldFromFile.RelStdDev),
              relativeStdDevUpdatable: isFMUUpdatable(gaussFieldFromFile.RelStdDev)
            })
          }

          const vario = new Variogram({
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

          await dispatch('gaussianRandomFields/addField',
            {
              field: new GaussianRandomField({
                name: gaussFieldFromFile._attributes.name,
                variogram: vario,
                trend: trend,
                crossSection: await dispatch('gaussianRandomFields/crossSections/fetch', { zone: zone, region: region }, { root: true }),
                zone: zone,
                region: region,
              })
            },
            { root: true }
          )
        })
      })
    },

    /**
     * Sets the facies probability for facies in zone. If the file spesifies probcubes, the method sets the
     * probablity to 1/number of fields in order to have the truncation rule visible after load
     * Note:
     * This will have to be updated in order to set correct selecton based on zone/region.
     * as it is now it just updates the facies over and over again for each zone/region combo
     *
     * @param dispatch
     * @param rootState
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateFaciesProbabilities: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      // zoneModelsFromFile.forEach(zoneModel => {
      for (const zoneModel of zoneModelsFromFile) {
        const useConstantProb = getBooleanValue(zoneModel.UseConstProb)
        const parent = getParent({ rootState }, zoneModel)
        // TODO: handle SimBoxThickness (must await implementation from Sindre on this?)
        const probCubes = []
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
            probCubes.push(probabilityCube)
            await dispatch('facies/changeProbabilityCube', { facies, probabilityCube }, { root: true })
          }
        }
        // hack to set value of preview probability of probCubes to 1/nr of probcubes to have the preview of the truncation rule load immediately
        // user can always push Average button and get the actual values from project.
        if (!useConstantProb) {
          await dispatch('facies/updateProbabilities', {
            probabilityCubes: probCubes.reduce((obj, name) => {
              obj[`${name}`] = 1 / probCubes.length
              return obj
            }, {})
          }, { root: true })
        }
      }
    },

    /**
     * Sets up Truncation Rules and connects them to fields as specified in the modelfile.
     * @param dispatch
     * @param rootState
     * @param rootGetters
     * @param zoneModelsFromFile
     * @returns {Promise<void>}
     */
    populateTruncationRules: async ({ dispatch, rootState }, zoneModelsFromFile) => {
      for (const zoneModel of zoneModelsFromFile) {
        const zoneNumber = parseInt(zoneModel._attributes.number)
        let regionNumber = parseInt(zoneModel._attributes.regionNumber)
        if (isNaN(regionNumber)) regionNumber = null

        const zone = Object.values(rootState.zones.available)
          .find(zone => zone.code === zoneNumber)
        const regionsForZone = rootState.zones.available[`${zone.id}`].regions
        const region = Object.values(regionsForZone)
          .find(region => region.code === regionNumber)

        const parent = {
          zone,
          region,
        }
        if (zoneModel.TruncationRule) {
          let truncationRuleContainer = zoneModel.TruncationRule
          let type = ''
          if (truncationRuleContainer.Trunc3D_Bayfill) {
            type = 'Bayfill'
            const rule = makeBayfillTruncationRule(truncationRuleContainer, rootState, parent)
            // now we should have everything needed to add the truncationRule.
            await dispatch('truncationRules/add', rule, { root: true })
          }
          // Changing presents must be done after the truncation rule is added (the command above must run to completion)
          // await dispatch('truncationRules/changePreset', { type, template: 'Imported', parent }, { root: true })
        }
      }
    }

  },

  mutations: {},

  getters: {},
}
