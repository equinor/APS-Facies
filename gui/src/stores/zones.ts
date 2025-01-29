import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Parent, Region, InstantiatedTruncationRule } from '@/utils/domain'
import { Zone } from '@/utils/domain'
import type { ID } from '@/utils/domain/types'
import { getId, includes } from '@/utils'
import { APSError } from '@/utils/domain/errors'
import rms from '@/api/rms'
import type {
  ZoneConfiguration,
  ZoneConformOption,
  ZoneSerialization,
} from '@/utils/domain/zone'
import { useRegionStore } from './regions'
import { useGaussianRandomFieldCrossSectionStore } from './gaussian-random-fields/cross-sections'
import type {
  CurrentIdentifiedStorePopulationData,
  CurrentIdentifiedStoreSerialization,
} from './utils/identified-items'
import { useCurrentIdentifiedItems } from './utils/identified-items'
import { useGridModelStore } from './grid-models'
import { useTruncationRuleStore } from './truncation-rules'
import { useFaciesStore } from './facies'

export type ZoneStorePopulationData = CurrentIdentifiedStorePopulationData<Zone>

export const useZoneStore = defineStore('zones', () => {
  const store = useCurrentIdentifiedItems<Zone>()
  const { available, identifiedAvailable, currentId, current } = store

  const loading = ref(false)

  function $reset() {
    store.$reset()
    loading.value = false
  }

  const selected = computed(() =>
    Object.keys(identifiedAvailable.value).filter(
      (id) => !!identifiedAvailable.value[id].selected,
    ),
  )

  const isFmuUpdatable = computed(() => {
    return (zone: Zone) => {
      const belongsToZone = (item: InstantiatedTruncationRule): boolean =>
        getId(item.parent.zone) === getId(zone) /* Ignore regions */

      const truncationRuleStore = useTruncationRuleStore()
      return (truncationRuleStore.available as InstantiatedTruncationRule[])
        .filter(belongsToZone)
        .some((rule) => rule.isFmuUpdatable)
    }
  })

  const byCode = computed(() => {
    return (zoneCode: number, regionNumber: number | null = null): Parent => {
      const zone = available.value.find((z) => z.code === zoneCode)
      if (!zone) throw new APSError(`There is no Zone with code ${zoneCode}`)
      const region = zone.regions.find((r) => r.code === regionNumber) ?? null
      if (regionNumber !== null && !region) {
        throw new APSError(
          `The Zone with code ${zoneCode}, does not have a region with code ${regionNumber}`,
        )
      }
      return {
        zone,
        region,
      }
    }
  })

  const byParent = computed(() => {
    return (parent: { zone: Zone | ID; region?: Region | ID | null }) => {
      const zone = identifiedAvailable.value[getId(parent.zone)]
      if (!parent.region) return zone
      return zone.regions.find((region) => region.id === getId(parent.region))
    }
  })

  function select(selected: Zone[]) {
    for (const zone of Object.values(identifiedAvailable.value)) {
      const toggled = includes(selected, zone)
      identifiedAvailable.value[zone.id].selected = toggled
    }
  }

  function setCurrentId(zoneId: ID) {
    const crossSectionStore = useGaussianRandomFieldCrossSectionStore()
    crossSectionStore.fetch(identifiedAvailable.value[zoneId])

    currentId.value = zoneId

    const truncationRuleStore = useTruncationRuleStore()
    truncationRuleStore.fetch()

    const faciesStore = useFaciesStore()
    faciesStore.selectObserved()
  }

  async function fetch() {
    loading.value = true

    const gridModelStore = useGridModelStore()
    if (!gridModelStore.current) {
      throw new APSError("Can't fetch zones without a current grid model.")
    }
    try {
      const zoneConfigurations = await rms.zones(gridModelStore.current.name)
      populate(zoneConfigurations)
    } finally {
      loading.value = false
    }
  }

  function populate(zoneConfigurations: ZoneConfiguration[]) {
    available.value = zoneConfigurations.map((zone) => new Zone(zone))
  }

  function setConformity(zone: Zone, conformity: ZoneConformOption) {
    identifiedAvailable.value[zone.id].conformity = conformity
  }

  function touch(parent: Parent) {
    const regionStore = useRegionStore()
    if (parent.region) {
      regionStore.touch(parent.region)
    } else {
      parent.zone.touch()
    }
  }

  return {
    available,
    identifiedAvailable,
    loading,
    currentId,
    current,
    selected,
    isFmuUpdatable,
    byCode,
    byParent,
    select,
    setCurrentId,
    fetch,
    populate,
    $reset,
    setConformity,
    touch,
  }
})

export type ZoneStoreSerialization =
  CurrentIdentifiedStoreSerialization<ZoneSerialization>

export function useZoneStoreSerialization(): ZoneStoreSerialization {
  const zoneStore = useZoneStore()
  return {
    available: zoneStore.available.map((zone) => zone.toJSON()),
    current: zoneStore.currentId,
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useZoneStore, import.meta.hot))
}
