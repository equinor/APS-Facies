import { v4 as uuidv4 } from 'uuid'

import type { Element } from '@/stores/utils/helpers'
import { removeOld, getElements } from '@/stores/utils/helpers'

import { APSError, APSTypeError } from '@/utils/domain/errors'

import type { ID } from '@/utils/domain/types'
import type { Dependent } from '@/utils/domain'
import { Region, Zone } from '@/utils/domain'
import type { ParentReference } from '@/utils/domain/bases/interfaces'
import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Parent, DependentConfiguration } from '@/utils/domain/bases/zoneRegionDependent'
import { getParentId } from '@/utils/domain/bases/zoneRegionDependent'
import { useRegionStore } from './regions'
import type { RegionSerialization, ZoneSerialization } from '@/utils/domain/zone'

type IDMapping = Map<ID, ID>

function getParent(item: Zone | Region): ParentReference {
  if (item instanceof Zone) {
    return {
      zone: item.id,
      region: null,
    }
  } else if (item instanceof Region) {
    return {
      zone: item.zone.id,
      region: item.id,
    }
  } else {
    throw new APSTypeError('The given item is not a Zone, nor a Region')
  }
}

function copyItems(
  element: Element,
  parent: ParentReference,
  idMapping: IDMapping,
): void {
  const items = element.items.filter((item): boolean =>
    item.isChildOf(parent),
  )
  items.forEach((item): void => {
    idMapping.set(item.id, uuidv4())
  })
  element.serialization = JSON.stringify(items)
}

function getIDMapping(
  source: ParentReference,
  target: ParentReference,
): IDMapping {
  const idMapping: IDMapping = new Map<ID, ID>()
  idMapping.set(JSON.stringify(source), JSON.stringify(target))
  return idMapping
}

function giveNewIds(
  elements: Element[],
  source: ParentReference,
  target: ParentReference,
): string {
  const idMapping = getIDMapping(source, target)
  const _serialization: Record<string, unknown> = {}
  for (const element of elements) {
    copyItems(element, source, idMapping)
    _serialization[element.name] = JSON.parse(element.serialization)
  }
  let serialization = JSON.stringify(_serialization)
  for (const [key, value] of idMapping) {
    const regex = new RegExp(key, 'gi') // Necessary to change _all_ occurrences, instead of just the first
    serialization = serialization.replace(regex, value)
  }
  return serialization
}

export const useCopyPasteStore = defineStore('copy-paste', () => {
  const source = ref<Zone | Region | null>()
  const _pasting = ref<{ [parentId: string]: boolean }>({})

  function $reset() {
    source.value = null
    _pasting.value = {}
  }

  const parent = computed(() => (source.value ? getParent(source.value) : null))
  const isPasting = computed(() => {
    return (parent: Zone | Region | Parent | ParentReference) => {
      if (parent instanceof Zone || parent instanceof Region) {
        parent = getParent(parent)
      }
      return _pasting.value[getParentId(parent)] ?? false
    }
  })

  function copy(newSource: Zone | Region | null) {
    source.value = newSource
  }

  function setPasting(source: ParentReference, toggle: boolean) {
    _pasting.value[getParentId(source)] = toggle
  }

  function paste(target: Zone | Region) {
    const targetParent = getParent(target)

    const regionStore = useRegionStore()
    const useRegions = regionStore.use

    if (useRegions && target instanceof Zone) {
      setPasting(targetParent, true)
      target.regions.forEach((region) => paste(region))
      setPasting(targetParent, false)
    } else {
      const source = parent.value
      if (source === null) throw new APSError("Can't paste when parent is null")

      setPasting(targetParent, true)
      const elements = getElements()

      removeOld(elements.toReversed(), targetParent)
      const serialization = giveNewIds(elements, source, targetParent)
      const actionMapping = elements.reduce((mapping, element) => ({
        ...mapping,
        [element.name]: {
          add: element.add,
          remove: element.remove,
        }
      }), {} as Record<string, {add: (item: DependentConfiguration) => void, remove: (item: Dependent) => void}>)
      for (const [key, items] of Object.entries(JSON.parse(serialization))) {
          (items as DependentConfiguration[]).forEach(
            (item) => actionMapping[key].add(item)
          )
      }
      setPasting(targetParent, false)
    }
  }

  return {
    source,
    _pasting,
    parent,
    isPasting,
    copy,
    paste,
    $reset,
  }
})

export type CopyPasteStoreSerialization = {
  source: ZoneSerialization | RegionSerialization | null
}

export function useCopyPaseSerialization(): CopyPasteStoreSerialization {
  const copyPaseStore = useCopyPasteStore()
  const source = copyPaseStore.source
  return {
    source: source ? source.toJSON() : null
  }
}

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useCopyPasteStore, import.meta.hot))
}
