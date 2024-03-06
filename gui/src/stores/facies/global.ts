import { acceptHMRUpdate, defineStore } from 'pinia'
import { GlobalFacies } from '@/utils/domain'
import type { CurrentIdentifiedStorePopulationData } from '@/stores/utils/identified-items'
import { useCurrentIdentifiedItems } from '@/stores/utils/identified-items'
import type { Ref } from 'vue'
import { computed, ref } from 'vue'
import { useFaciesStore } from '.'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useRegionStore } from '@/stores/regions'
import { useParameterRegionStore } from '@/stores/parameters/region'
import type { RmsFacies } from '@/api/types'
import type { Color } from '@/utils/domain/facies/helpers/colors'
import { useConstantsFaciesColorsStore } from '@/stores/constants/facies-colors'
import { isEmpty } from '@/utils'
import { APSError } from '@/utils/domain/errors'
import type { ID } from '@/utils/domain/types'
import { displayWarning } from "@/utils/helpers/storeInteraction";

export type FaciesGlobalStorePopulationData =
  CurrentIdentifiedStorePopulationData<GlobalFacies>

interface FaciesSpecification extends RmsFacies {
  color?: Color
}

export const useGlobalFaciesStore = defineStore('facies-global', () => {
  const store = useCurrentIdentifiedItems<GlobalFacies>()
  const { identifiedAvailable, available, addAvailable, currentId, current, removeAvailable } = store

  const loading = ref(false)
  const rmsFacies = ref([]) as Ref<RmsFacies[]>

  const selected = computed(() => {
    const faciesStore = useFaciesStore()
    return faciesStore.selected.map(
      (facies) => identifiedAvailable.value[facies.facies.id],
    )
  })

  const byId = computed<(id: ID) => GlobalFacies | null>(() => {
    return (id: ID) => identifiedAvailable.value[id] ?? null
  })

  async function _getFaciesFromRms(warnIfInvalid = false) {
    const blockedWellStore = useParameterBlockedWellStore()
    const blockedWellLogStore = useParameterBlockedWellLogStore()

    if (
      blockedWellStore.selected === null ||
      blockedWellLogStore.selected === null
    ) {
      if (warnIfInvalid) {
        displayWarning('Could not fetch facies from RMS; blocked well (log) is not set')
        return []
      }
      throw new APSError(
        'Both blockedWellStore and blockedWellLogStore must be set when fetching rms facies',
      )
    }
    const gridModelStore = useGridModelStore()
    const regionStore = useRegionStore()
    const parameterRegionStore = useParameterRegionStore()

    return await rms.facies(
      gridModelStore.current!.name,
      blockedWellStore.selected,
      blockedWellLogStore.selected,
      regionStore.use
        ? parameterRegionStore.selected
        : '__REGIONS_NOT_IN_USE__',
    )
  }

  async function fetch() {
    $reset()

    loading.value = true
    const fetchedFacies = await _getFaciesFromRms()
    loading.value = false

    populate(fetchedFacies)

    rmsFacies.value = fetchedFacies
  }

  function populate(facies: FaciesSpecification[]) {
    const faciesColorStore = useConstantsFaciesColorsStore()

    const minFaciesCode = Math.min(...facies.map(({ code }) => code))
    for (const f of facies) {
      f.color = f.color ?? faciesColorStore.byCode(f.code - minFaciesCode)
    }
    const existingFacies = available.value.reduce((mapping, facies) => ({
      ...mapping,
      [facies.code]: facies,
    }), {} as Record<number, GlobalFacies>)
    facies
      .forEach(configuration => {
        const existing = existingFacies[configuration.code]
        if (!existing) {
          available.value.push(new GlobalFacies(configuration as FaciesSpecification & {
            color: Color // We add a color if one is not given
          }))
        } else {
          // The global facies are first fetched when blocked well log is selected
          // This is when we execute the logic for showing which facies are observed in RMS
          Object.assign(existing, configuration)
        }
      })
  }

  function $reset() {
    store.$reset()
    loading.value = false
    rmsFacies.value = []
  }

  async function refresh() {
    const codeFaciesMapping = available.value.reduce(
      (mapping, facies) => mapping.set(facies.code, facies),
      new Map<number, GlobalFacies>(),
    )

    const rmsFacies = await _getFaciesFromRms(true)
    rmsFacies
      .filter(({ code }) => !codeFaciesMapping.has(code))
      .forEach((f) => create(f))

    // Comment from vuex REFRESH mutation:
    // Update global facies in place, to preserve references, and thus comparison between GlobalFacies
    // and anything else, that might reference one (such as Facies, FaciesGroup, and truncation rules, though polygons)
    // PS: Doing this functionally, i.e. creating new objects, quickly became complex, once the truncation rules
    //     had to be created anew as well
    for (const facies of available.value) {
      Object.assign(
        facies,
        rmsFacies.find(({ code }) => code === facies.code) ?? {},
      )
    }
  }

  function create({
    code,
    name,
    color,
    observed,
  }: Partial<FaciesSpecification>) {
    if (isEmpty(code) || code < 0) {
      code = Math.max(
        0, // Avoid -infinity if there is no facies from RMS
        ...(available.value as { code: number }[])
          .concat(rmsFacies.value)
          .map((f) => f.code),
      ) + 1
    }
    name = name ?? `F${code}`

    const faciesColorStore = useConstantsFaciesColorsStore()
    color = color ?? faciesColorStore.byCode(code)

    if (
      rmsFacies.value.find(
        (rmsFacies) => rmsFacies.code === code && rmsFacies.name === name,
      )
    ) {
      throw new APSError(
        `There already exists a facies with code = ${code}, or name = ${name} in RMS`,
      )
    }
    const facies = new GlobalFacies({ code, name, color, observed })
    addAvailable(facies)
    return facies
  }

  function setCurrentId(id: ID | null) {
    currentId.value = id
  }

  function removeSelectedFacies() {
    if (current.value !== null) {
      removeAvailable(current.value)
      setCurrentId(null)
    }
  }

  function changeColorPalette(mapping: Map<Color, Color>) {
    for (const globalFacies of available.value) {
      const newColor = mapping.get(globalFacies.color)
      if (!newColor) throw new Error(`${globalFacies.color} isn't in mapping.`)
      globalFacies.color = newColor
    }
  }

  return {
    ...store,
    byId,
    rmsFacies,
    selected,
    loading,
    fetch,
    populate,
    $reset,
    refresh,
    create,
    setCurrentId,
    removeSelectedFacies,
    changeColorPalette,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useGlobalFaciesStore, import.meta.hot))
}
