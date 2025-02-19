import { acceptHMRUpdate, defineStore } from 'pinia'
import {
  type IdentifiedStorePopulationData,
  useIdentifiedItems,
} from '@/stores/utils/identified-items'
import { FaciesGroup } from '@/utils/domain'
import type { Facies, Parent } from '@/utils/domain'
import { computed } from 'vue'
import { getId } from '@/utils'
import type { ID } from '@/utils/domain/types'
import type { Identifiable } from '@/utils/domain/bases/interfaces'
import { useFaciesStore } from '.'
import type {
  FaciesGroupConfiguration,
  FaciesGroupSerialization,
} from '@/utils/domain/facies/group'
import { resolveParentReference } from '@/stores/utils'
import { APSError } from '@/utils/domain/errors'

export type FaciesGroupStorePopulationData =
  IdentifiedStorePopulationData<FaciesGroup>

export const useFaciesGroupStore = defineStore('facies-groups', () => {
  const {
    available,
    identifiedAvailable,
    addAvailable,
    removeAvailable,
    $reset,
  } = useIdentifiedItems<FaciesGroup>()

  const byId = computed(() => {
    return (id: ID | Identifiable) => identifiedAvailable.value[getId(id)]
  })

  const byFacies = computed(() => {
    return (facies: Facies[], parent: Parent) =>
      available.value.find(
        (group) => group.isChildOf(parent) && group.contains(facies),
      )
  })

  const isUsed = computed(() => {
    return (facies: Facies) => {
      for (const group of available.value) {
        for (const groupFacies of group.facies) {
          if (groupFacies.id === facies.id) return true
        }
      }
      return false
    }
  })

  function populate(groupConfigs: FaciesGroupSerialization[]) {
    const faciesStore = useFaciesStore()
    available.value = groupConfigs.map(
      (groupConfig) =>
        new FaciesGroup({
          ...groupConfig,
          facies: groupConfig.facies.map((f) =>
            faciesStore.byId(f),
          ) as Facies[],
          parent: resolveParentReference(groupConfig.parent),
        }),
    )
  }

  function get(facies: Facies[], parent: Parent) {
    if (facies.length === 0) {
      throw new APSError('Empty facies list')
    }
    const group = byFacies.value(facies, parent)
    if (group) return group

    return add(facies, parent)
  }

  function add(
    facies: FaciesGroupConfiguration['facies'],
    parent: Parent,
    id?: ID,
  ) {
    if (facies.some((f): boolean => isUsed.value(f))) {
      throw new Error(`The facies, ${facies}, has already been specified`)
    }
    if (!parent || !parent.zone) {
      throw new Error(
        `The facies, ${facies}, does not belong to a given zone / region`,
      )
    }

    const group = new FaciesGroup({
      id,
      facies,
      ...parent,
    })
    addAvailable(group)
    return group
  }

  function update(group: FaciesGroup, facies: Facies[]) {
    identifiedAvailable.value[group.id].facies = facies
  }

  return {
    available,
    identifiedAvailable,
    byId,
    byFacies,
    isUsed,
    populate,
    get,
    add,
    remove: removeAvailable,
    update,
    $reset,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useFaciesGroupStore, import.meta.hot))
}
