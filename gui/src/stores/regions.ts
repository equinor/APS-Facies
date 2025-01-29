import { acceptHMRUpdate, defineStore } from 'pinia'
import type { Zone } from '@/utils/domain'
import { Region } from '@/utils/domain'
import rms from '@/api/rms'
import { computed, ref } from 'vue'
import type { ID } from '@/utils/domain/types'
import { includes, notEmpty } from '@/utils'
import { useZoneStore } from './zones'
import { useFaciesStore } from './facies'
import { useGaussianRandomFieldCrossSectionStore } from './gaussian-random-fields/cross-sections'
import type { CurrentIdentifiedStorePopulationData } from './utils/identified-items'
import { useGridModelStore } from './grid-models'
import { APSError } from '@/utils/domain/errors'
import { useTruncationRuleStore } from './truncation-rules'
import { useParameterRegionStore } from './parameters/region'

export type RegionStorePopulationData =
  CurrentIdentifiedStorePopulationData<Region> & { use?: boolean }

export const useRegionStore = defineStore('regions', () => {
  const use = ref(false)
  const loading = ref(false)
  const currentId = ref<string | null>(null)

  const current = computed<Region | null>(() => {
    for (const zone of useZoneStore().available) {
      for (const region of zone.regions) {
        if (region.id === currentId.value) {
          return region as Region
        }
      }
    }
    return null
  })

  function $reset() {
    currentId.value = null
    use.value = false
    loading.value = false
  }

  async function fetchRegions(zone: Zone) {
    const gridModelStore = useGridModelStore()
    if (!gridModelStore.current) {
      throw new APSError("Can't fetch regions without a current grid model.")
    }
    const parameterRegionStore = useParameterRegionStore()
    if (parameterRegionStore.selected === null) {
      throw new APSError("Can't fetch regions without regionParameter")
    }
    const rmsRegions = await rms.regions(
      gridModelStore.current.name,
      zone.name,
      parameterRegionStore.selected,
    )
    for (const rmsRegion of rmsRegions) {
      const exists = zone.regions.find(
        ({ code, name }): boolean =>
          rmsRegion.code === code && rmsRegion.name === name,
      )
      if (!exists) {
        const newRegion = new Region({
          ...rmsRegion,
          selected: !!zone.selected,
          zone,
        })
        zone.regions = [...zone.regions, newRegion]
      }
    }
  }
  function select(regions: Region[]) {
    const affectedZones = regions.reduce(
      (unique, region) => unique.add(region.zone),
      new Set<Zone>(),
    )
    for (const zone of affectedZones) {
      for (const region of zone.regions) {
        const regionZoneRegion = region.zone.regions.find(
          (r) => r.id === region.id,
        )
        if (regionZoneRegion)
          regionZoneRegion.selected = includes(regions, region)
      }
    }
    // All regions of, presumably, the current zone has been deselected
    if (regions.length === 0) {
      const zoneStore = useZoneStore()
      if (zoneStore.current) {
        zoneStore.current.selected = false
      }
    }
  }

  function setCurrentId(id: ID) {
    const zoneStore = useZoneStore()
    const zone = zoneStore.available.find((zone) =>
      zone.regions.some((region) => region.id === id),
    )
    if (!zone)
      throw new Error(
        `There are no zones corresponding with the region with ID '${id}'`,
      )

    const region = zone.regions.find((region) => region.id === id)
    if (!region)
      throw new Error(
        `The region with ID ${id} was not found in its respective zone (${zone})`,
      )

    const crossSectionStore = useGaussianRandomFieldCrossSectionStore()
    crossSectionStore.fetch(zone as Zone, region as Region)

    currentId.value = id

    const truncationRuleStore = useTruncationRuleStore()
    truncationRuleStore.fetch()

    // Select the observed facies
    const faciesStore = useFaciesStore()
    faciesStore.selectObserved()
  }

  async function fetch() {
    const zoneStore = useZoneStore()
    const parameterRegionStore = useParameterRegionStore()
    if (use.value && notEmpty(parameterRegionStore.selected)) {
      loading.value = true
      for (const zone of zoneStore.available) {
        zone.regions = []
        await fetchRegions(zone as Zone)
      }
      loading.value = false
    }
  }

  async function setUse(newUse: boolean, doFetch: boolean = true) {
    use.value = newUse
    currentId.value = null
    if (doFetch) await fetch()
  }

  function populate(configurations: RegionStoreSerialization) {
    use.value = configurations.use
    currentId.value = configurations.current
  }

  function touch(region: Region) {
    region.touch()
  }

  return {
    currentId,
    use,
    loading,
    current,
    select,
    setCurrentId,
    fetch,
    setUse,
    populate,
    touch,
    $reset,
  }
})

export interface RegionStoreSerialization {
  use: boolean
  current: ID | null
}
export function useRegionStoreSerialization(): RegionStoreSerialization {
  const regionStore = useRegionStore()
  return {
    use: regionStore.use,
    current: regionStore.currentId,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useRegionStore, import.meta.hot))
}
