export default {
  namespaced: true,

  state: {},

  modules: {},

  actions: {
    populateGUI: ({ dispatch }, json) => {
      const apsModelContainer = JSON.parse(json)
      // TODO: Add a helpermethod to get text value of node when method resolve from other branch gets into develop, like
      // import { resolve } from '@/utils'
      // const helper = (container, prop) => {
      //   let value = resolve(prop, container.APSModel)
      //   if (value._text) {
      //     value = value._text.trim()
      //   }
      //   return value
      // }
      // so that instead of
      // dispatch('gridModels/select', apsModelContainer.APSModel.GridModelName._text.trim(), { root: true })
      // we can use
      // dispatch('gridModels/select', helper(apsModelContainer, 'GridModelName'), { root: true })
      dispatch('gridModels/select', apsModelContainer.APSModel.GridModelName._text.trim(), { root: true })
        .then(() => {
          dispatch(`parameters/zone/select`, apsModelContainer.APSModel.ZoneParamName._text.trim(), { root: true })
            .then(() => {
              if (apsModelContainer.APSModel.RegionParamName) {
                dispatch(`parameters/region/select`, apsModelContainer.APSModel.RegionParamName._text.trim(), { root: true })
                  .then(() => {
                    dispatch('selectZonesAndRegions', apsModelContainer.APSModel.ZoneModels.Zone)
                  })
              } else {
                dispatch('selectZonesAndRegions', apsModelContainer.APSModel.ZoneModels.Zone)
              }
            })
        })
        .catch(reason => {
          alert(reason)
        })
    },
    selectZonesAndRegions: ({ dispatch, rootState }, zoneModelsFromFile) => {
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

      // testprinting what to select
      // for (const item of zoneRegionsMap) {
      //  console.log('zone ' + item[0])
      //  item[1].forEach(region => {
      //    console.log(' region ' + region)
      //  })
      // }

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
              const regionIdFromFile = regionsInZone[i]
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
      dispatch('zones/current', zoneToSetAsCurrent, { root: true })
      dispatch('zones/select', zonesToSelect, { root: true })
      if (regionToSetAsCurrent) {
        dispatch('regions/current', regionToSetAsCurrent, { root: true })
        dispatch('regions/select', regionsToSelect, { root: true })
      }
    }
  },

  mutations: {},

  getters: {},
}
