import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed } from 'vue'
import CrossSection, {
  type CrossSectionSerialization,
  type CrossSectionType,
} from '@/utils/domain/gaussianRandomField/crossSection'
import { getId } from '@/utils'
import type { ID } from '@/utils/domain/types'
import type { GaussianRandomField, Parent, ParentReference, Region, Zone } from '@/utils/domain'
import type { Optional } from '@/utils/typing'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { DEFAULT_CROSS_SECTION } from '@/config'
import { useGaussianRandomFieldStore } from '.'
import { APSError } from '@/utils/domain/errors'
import { useZoneRegionDependentStore } from '@/stores/utils/zone-region-dependent-items'
import type { AvailableOptionSerialization } from '@/stores/parameters/serialization/helpers'

export const useGaussianRandomFieldCrossSectionStore = defineStore(
  'gaussian-random-field-cross-sections',
  () => {
    const store = useZoneRegionDependentStore<CrossSection>()
    const {
      available,
      identifiedAvailable,
      addAvailable,
      removeAvailable,
      $reset,
    } = store

    const byParent = computed(() => {
      return (parent: Parent | ParentReference) =>
        available.value.find((item) => item.isChildOf(parent)) ?? null
    })

    const byId = computed(() => {
      return (id: ID) => identifiedAvailable.value[id]
    })

    function fetch(
      zone: Optional<Zone> = null,
      region: Optional<Region> = null,
    ): CrossSection {
      if (!zone) {
        zone = useZoneStore().current as Zone | null
      }
      if (!zone) throw new APSError('No Zone selected')
      if (!region) {
        region = useRegionStore().current as Region | null
      }
      const parent: Parent = {
        zone,
        region,
      }
      if (!parent.zone) throw new APSError('No Zone provided')
      const existing = byParent.value(parent)
      if (existing) return existing

      return add({
        type: DEFAULT_CROSS_SECTION.type,
        parent,
      } as CrossSection)
    }

    const current = computed<CrossSection>({
      get: () => {
        const existing = store.current.value
        if (existing) return existing
        return fetch()
      },
      set: (value: CrossSection) => {
        store.current.value = value
      }
    })

    function populate(sections: CrossSectionSerialization[]) {
      const gaussianRandomFieldStore = useGaussianRandomFieldStore()
      for (const section of sections) {
        const existing = byParent.value(section.parent)
        if (existing && existing.id !== section.id) {
          if (
            gaussianRandomFieldStore.available.some(
              (field) => field.settings.crossSection.id === existing.id,
            )
          ) {
            throw new APSError('There is a conflict with the cross sections')
          }
          removeAvailable(existing)
        }
        add(section)
      }
    }

    function add(section: CrossSection | CrossSectionSerialization): CrossSection {
      const zoneStore = useZoneStore()
      const regionStore = useRegionStore()
      const parent = {
        zone: zoneStore.identifiedAvailable[getId(section.parent.zone)],
        region: section.parent.region
          ? regionStore.identifiedAvailable[getId(section.parent.region)]
          : null,
      }
      const existing = byParent.value(parent)
      if (!existing) {
        const newSection = new CrossSection({ ...section, parent })
        addAvailable(newSection)
        return newSection
      }
      return existing
    }

    function remove(section: CrossSection) {
      const fieldStore = useGaussianRandomFieldStore()
      const relevantFields = fieldStore.available.filter(
        (field) => getId(field.settings.crossSection) === getId(section),
      ) as GaussianRandomField[]
      relevantFields.forEach((field) => fieldStore.remove(field))

      removeAvailable(section)
    }

    async function changeType(type: CrossSectionType) {
      const section = current.value
      section.type = type

      const fieldStore = useGaussianRandomFieldStore()
      const relevantFields = fieldStore.available.filter(
        (field) => getId(field.settings.crossSection) === getId(section),
      ) as GaussianRandomField[]

      await Promise.all(
        relevantFields.map((field) => fieldStore.updateSimulation(field)),
      )
    }

    return {
      available,
      identifiedAvailable,
      add,
      remove,
      current,
      byParent,
      byId,
      $reset,
      fetch,
      populate,
      changeType,
    }
  },
)

export type GaussianRandomFieldCrossSectionStoreSerialization = AvailableOptionSerialization<CrossSectionSerialization>
export function useGaussianRandomFieldCrossSectionStoreSerialization(): GaussianRandomFieldCrossSectionStoreSerialization {
    const { available } = useGaussianRandomFieldCrossSectionStore()
    return {
        available: available.map(crossSection => crossSection.toJSON()),
    }
}

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useGaussianRandomFieldCrossSectionStore, import.meta.hot),
  )
}
