import { acceptHMRUpdate, defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { Identifiable, Identified } from '@/utils/domain/bases/interfaces'
import type { Parent, Region, Zone, InstantiatedTruncationRule, Polygon } from '@/utils/domain'
import { Facies, GlobalFacies } from '@/utils/domain'
import type {
  FaciesSerialization,
  ProbabilityCube,
} from '@/utils/domain/facies/local'
import type { ID, PROBABILITY } from '@/utils/domain/types'
import { getId, hasParents, isEmpty, notEmpty, parentId } from '@/utils'
import { getRelevant } from '@/stores/utils/helpers'
import { isNumber } from 'lodash'
import type GridModel from '@/utils/domain/gridModel'
import type { IdentifiedStorePopulationData } from '@/stores/utils/identified-items'
import {
  useIdentifiedItems,
} from '@/stores/utils/identified-items'
import { useRootStore } from '@/stores'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'
import { useGridModelStore } from '@/stores/grid-models'
import { useParameterRegionStore } from '@/stores/parameters/region'
import rms from '@/api/rms'
import { divide } from 'mathjs'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import { useOptionStore } from '@/stores/options'
import { resolveParentReference } from '@/stores/utils'
import { useGlobalFaciesStore } from './global'
import { useFaciesGroupStore } from './groups'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import type { PolygonSerialization, PolygonSpecification } from "@/utils/domain/polygon/base";
import type OverlayTruncationRule from "@/utils/domain/truncationRule/overlay";

export type FaciesStorePopulationData = IdentifiedStorePopulationData<Facies>

function removeUnavailableFaciesFromTruncationRule(globalFacies: GlobalFacies[], parent: Parent) {
  const { available } = useTruncationRuleStore()
  const relevantTruncationRule = (available as InstantiatedTruncationRule[]).find((rule: InstantiatedTruncationRule) => hasParents(rule, parent.zone, parent.region))
  const globalFaciesCodes = new Set(globalFacies.map(({code}) => code))
  if (relevantTruncationRule) {
    relevantTruncationRule.polygons.forEach(polygon => {
      if (polygon.facies && !globalFaciesCodes.has(polygon.facies.code)) {
        polygon.facies = null
      }
    })
  }
}

export const useFaciesStore = defineStore('facies', () => {
  const store = useIdentifiedItems<Facies>()
  const { available, identifiedAvailable, addAvailable, removeAvailable } = store
  const _constantProbability = ref<Identified<boolean>>({})

  const byId = computed(() => {
    return (item: ID | Identifiable): Facies | Facies[] | null => {
      const globalStore = useGlobalFaciesStore()
      const groupsStore = useFaciesGroupStore()
      const id = getId(item)
      // TODO: Make this always return single Facies, and add seperate functions
      // for GlobalFacies and FaciesGroup.
      const facies =
        identifiedAvailable.value[id] ?? globalStore.identifiedAvailable[id]
      if (!facies) {
        const group = groupsStore.byId(id)
        return group?.facies.map(
          (groupFacies) => byId.value(groupFacies) as Facies,
        )
      } else {
        return facies || null
      }
    }
  })

  const byName = computed(() => {
    return (name: string) =>
      available.value.find((facies) => facies.name === name)
  })

  const constantProbability = computed(() => {
    return (parent: Parent) =>
      _constantProbability.value[parentId(parent)] ?? true
  })

  const selected = computed(() => {
    const { current: zone } = useZoneStore()
    const { current: region } = useRegionStore()
    if (!zone) return []

    return getRelevant(available.value, { zone, region } as Parent)
      .sort((a, b) => a.facies.code - b.facies.code)
  })

  const cumulative = computed(() =>
    selected.value
      .map((facies) => facies.previewProbability ?? 0)
      .reduce((sum, prob) => sum + prob, 0),
  )

  const unset = computed(() =>
    selected.value.every((facies) => !isNumber(facies.previewProbability)),
  )

  const availableForBackgroundFacies = computed(() => {
    const groupsStore = useFaciesGroupStore()
    return <T extends Polygon,
    S extends PolygonSerialization,
    P extends PolygonSpecification,
    RULE extends OverlayTruncationRule<T, S, P>,
  >(rule: RULE, facies: Facies) =>
      !groupsStore.isUsed(facies) &&
      rule.backgroundPolygons
        .map((polygon) => getId(polygon.facies))
        .includes(getId(facies))
  })

  const isFromRMS = computed(() => {
    const globalStore = useGlobalFaciesStore()
    return (facies: GlobalFacies | null): boolean =>
      (facies &&
      !!globalStore.rmsFacies.find(
        (f) => f.code === facies.code && f.name === facies.name,
      )) ?? false
  })

  // TODO: rename to "are" or "have been"
  const isFaciesFetchedFromRMS = computed(() => {
    const parameterBlockedWellStore = useParameterBlockedWellStore()
    const parameterBlockedWellLogStore = useParameterBlockedWellLogStore()
    return (
      !!parameterBlockedWellStore.selected &&
      !!parameterBlockedWellLogStore.selected
    )
  })

  function add(
    globalFacies: GlobalFacies | ID,
    parent: Parent,
    probabilityCube: ProbabilityCube | null = null,
    previewProbability: PROBABILITY | null = null,
    id: ID | null = null,
  ) {
    const facies = globalFacies instanceof GlobalFacies
          ? globalFacies
          : byId.value(globalFacies)
    if (!(facies instanceof GlobalFacies)) {
      throw new Error("The given facies is not a valid GlobalFacies")
    }
    const localFacies = new Facies({
      id: id ?? undefined,
      // surely facies: Facies will never be GlobalFacies? if so, we should re-type it?
      // and doing byId(facies) signifies that it's an ID, so really it's either a
      // GlobalFacies or ID?
      facies,
      probabilityCube,
      previewProbability,
      parent,
    })
    addAvailable(localFacies)
    return localFacies
  }

  function select(globalFacies: GlobalFacies[], parent: Parent) {
    const relevantFacies = getRelevant(available.value, parent)

    let removed = false
    for (const global of globalFacies) {
      if (
        !relevantFacies
          .map((facies) => getId(facies.facies))
          .includes(getId(global))
      ) {
        add(global, parent)
      }
    }
    for (const facies of relevantFacies) {
      if (!globalFacies.map(getId).includes(getId(facies.facies))) {
        removeAvailable(facies)
        removed = true
      }
    }
    const newRelevantFacies = getRelevant(available.value, parent)
    if (removed) normalize(newRelevantFacies)

    const zoneStore = useZoneStore()
    zoneStore.touch(parent)
    removeUnavailableFaciesFromTruncationRule(globalFacies, parent)
  }

  function selectObserved() {
    const rootStore = useRootStore()
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    const globalStore = useGlobalFaciesStore()
    const optionStore = useOptionStore()

    if (rootStore.loading) return
    if (!optionStore.options.automaticObservedFaciesSelection) return
    const zone = zoneStore.current
    const region = regionStore.current
    const parentDefined = regionStore.use ? !!region : !!zone

    if (parentDefined && isFaciesFetchedFromRMS.value) {
      const parent = { zone: zone as Zone, region } as Parent
      const touched =
        (regionStore.use ? region?.touched : zone?.touched) ?? false

      if (!touched) {
        const observedFacies = (globalStore.available as GlobalFacies[]).filter(
          (globalFacies) =>
            globalFacies.isObserved(parent) && isFromRMS.value(globalFacies),
        )
        if (observedFacies.length > 0) {
          select(observedFacies, parent)
        }
      }
    }
  }

  function populate(faciesSerializations: FaciesSerialization[]) {
    const globalStore = useGlobalFaciesStore()
    available.value = faciesSerializations.map(
      (serialization) => {
        const globalFacies = globalStore.byId(getId(serialization.facies))
        if (!globalFacies) {
          throw new Error(`Could not find facies with ID '${serialization.facies}'`)
        }
        return new Facies({
          ...serialization,
          facies: globalFacies,
          parent: resolveParentReference(serialization.parent),
        })
      },
    )
  }

  function updateProbabilities(
    cubeAverages: Record<ProbabilityCube, number>,
    parent: Parent,
  ) {
    if (isEmpty(cubeAverages)) return
    const relevantFacies = available.value.filter(
      (f) => f.isChildOf(parent) && f.probabilityCube !== null,
    )
    for (const facies of relevantFacies) {
      const previewProb = cubeAverages[facies.probabilityCube!]
      identifiedAvailable.value[facies.id].previewProbability = previewProb
    }
    normalize(relevantFacies)
  }

  function normalizeEmpty() {
    const selectedFacies = selected.value
    const probabilities = selectedFacies.map((f) => f.previewProbability ?? 0)
    const probabilitySum = probabilities.reduce((sum, prob) => sum + prob, 0)
    const zeroProbabilityCount = probabilities.filter((p) => p === 0).length
    const emptyProbability = (1 - probabilitySum) / zeroProbabilityCount

    for (const f of selectedFacies.filter((f) => !f.previewProbability)) {
      f.previewProbability = emptyProbability
    }
  }

  async function averageProbabilityCubes({
    probabilityCubes = undefined,
    gridModel = undefined,
    zoneNumber = undefined,
    useRegions = undefined,
    regionParameter = undefined,
    regionNumber = undefined,
  }: {
    probabilityCubes?: ProbabilityCube[]
    gridModel?: GridModel
    zoneNumber?: number
    useRegions?: boolean
    regionParameter?: string
    regionNumber?: number | null
  }) {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    const gridModelStore = useGridModelStore()
    const parameterRegionStore = useParameterRegionStore()

    if (!gridModel) gridModel = gridModelStore.current! as GridModel
    if (!zoneNumber && zoneNumber !== 0) zoneNumber = zoneStore.current!.code
    if (useRegions === null) useRegions = regionStore.use
    if (useRegions) {
      if (!regionParameter)
        regionParameter = parameterRegionStore.selected ?? undefined
      const region = regionStore.current as Region
      if (region && !regionNumber && regionNumber !== 0)
        regionNumber = region.code
    }

    const parent = zoneStore.byCode(
      zoneNumber,
      useRegions ? regionNumber : null,
    )

    if (!probabilityCubes) {
      probabilityCubes = available.value
        .filter((facies) => facies.isChildOf(parent))
        .map((facies) => facies.probabilityCube)
        .filter(notEmpty)
    }
    // Result in the form of { probCubeName_1: average, ...}
    const cubeAverages = await rms.averageProbabilityCubes(
      gridModel.name,
      probabilityCubes,
      zoneNumber,
      regionParameter,
      regionNumber,
    )

    updateProbabilities(cubeAverages, parent)
  }

  function normalize(selectedFacies: Facies[] | null = null) {
    selectedFacies = selectedFacies ?? selected.value

    const cumulativeProbability = selectedFacies
      .map((facies) => facies.previewProbability)
      .reduce((sum, prob) => sum! + (prob ?? 0), 0)
    selectedFacies
      .filter((facies) => facies.previewProbability !== null)
      .map((facies) => {
        const probability = !cumulativeProbability
          ? divide(1, selectedFacies!.length)
          : divide(facies.previewProbability || 0, cumulativeProbability)
        return changePreviewProbability(facies, probability)
      })
  }

  function populateConstantProbability(parentToggledness: Record<ID, boolean>) {
    for (const parentId in parentToggledness) {
      _constantProbability.value[parentId] = parentToggledness[parentId]
    }
  }

  function toggleConstantProbability() {
    const zoneStore = useZoneStore()
    const regionStore = useRegionStore()
    const parent = {
      zone: zoneStore.current!,
      region: regionStore.current,
    } as Parent
    const _id = parentId(parent)
    const currentUsage = constantProbability.value(parent)
    _constantProbability.value[_id] = !currentUsage
  }

  function setConstantProbability(parentId: ID, usage: boolean) {
    _constantProbability.value[parentId] = usage
  }

  function changeProbabilityCube(facies: Facies, cube: ProbabilityCube) {
    facies.probabilityCube = cube
  }

  function changePreviewProbability(facies: Facies, probability: PROBABILITY | null) {
    facies.previewProbability = probability
  }

  async function fetch() {
    const globalStore = useGlobalFaciesStore()
    await globalStore.fetch()
  }

  function $reset() {
    store.$reset()
    useGlobalFaciesStore()
      .$reset()
    useFaciesGroupStore()
      .$reset()
    _constantProbability.value = {}
  }

  return {
    available,
    identifiedAvailable,
    byId,
    byName,
    constantProbability,
    selected,
    cumulative,
    unset,
    availableForBackgroundFacies,
    isFromRMS,
    isFaciesFetchedFromRMS,
    add,
    remove: removeAvailable,
    select,
    selectObserved,
    populate,
    updateProbabilities,
    normalizeEmpty,
    averageProbabilityCubes,
    normalize,
    populateConstantProbability,
    toggleConstantProbability,
    setConstantProbability,
    changeProbabilityCube,
    changePreviewProbability,
    fetch,
    $reset,
  }
})

if (import.meta.hot) {
  import.meta.hot.accept(acceptHMRUpdate(useFaciesStore, import.meta.hot))
}
