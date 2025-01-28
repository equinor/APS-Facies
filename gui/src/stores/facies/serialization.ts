import { useFaciesStore } from '@/stores/facies/index'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import type { FaciesSerialization } from '@/utils/domain/facies/local'
import type { Identified } from '@/utils/domain/bases/interfaces'
import { useZoneStore } from '@/stores/zones'
import { parentId } from '@/utils'
import type { Parent } from '@/utils/domain'
import type { GlobalFaciesSerialization } from '@/utils/domain/facies/global'
import type { FaciesGroupSerialization } from '@/utils/domain/facies/group'

function useConstantProbabilitySerialization(): Identified<boolean> {
  const { constantProbability } = useFaciesStore()
  const zoneStore = useZoneStore()
  const constantProbabilities = {} as Identified<boolean>
  zoneStore.available.forEach((zone) => {
    if (zone.hasRegions) {
      zone.regions.forEach((region) => {
        const parent = { zone, region } as Parent
        constantProbabilities[parentId(parent)] = constantProbability(parent)
      })
    } else {
      const parent = { zone } as Parent
      constantProbabilities[parentId(parent)] = constantProbability(parent)
    }
  })
  return constantProbabilities
}
export interface FaciesStoreSerialization {
  available: FaciesSerialization[]
  constantProbability: Identified<boolean>
  global: {
    available: GlobalFaciesSerialization[]
  }
  groups: {
    available: FaciesGroupSerialization[]
  }
}

export function useFaciesStoreSerialization(): FaciesStoreSerialization {
  const localFaciesStore = useFaciesStore()
  const globalFaciesStore = useGlobalFaciesStore()
  const faciesGroupStore = useFaciesGroupStore()

  return {
    available: localFaciesStore.available.map((facies) => facies.toJSON()),
    constantProbability: useConstantProbabilitySerialization(),
    global: {
      available: globalFaciesStore.available.map((facies) => facies.toJSON()),
    },
    groups: {
      available: faciesGroupStore.available.map((facies) => facies.toJSON()),
    },
  }
}
