import { acceptHMRUpdate, defineStore } from 'pinia'
import { useSelectableChoice } from './utils/selectable-choice'
import rms from '@/api/rms'
import { useGridModelStore } from '@/stores/grid-models'
import type { Facies, FaciesGroup, Parent } from '@/utils/domain'
import { useZoneStore } from '@/stores/zones'
import { useFaciesStore } from '@/stores/facies'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { useFaciesGroupStore } from '@/stores/facies/groups'
import { useGlobalFaciesStore } from '@/stores/facies/global'
import { useParameterBlockedWellStore } from './blocked-well'
import type { TruncationRule } from '@/utils/domain/truncationRule'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type Polygon from '@/utils/domain/polygon/base'
import { ref } from 'vue'

export const useParameterBlockedWellLogStore = defineStore(
  'parameter-blocked-well-log',
  () => {
    const { available, selected, $reset } = useSelectableChoice<string>()
    const loading = ref(false)

    function _removeFaciesDependent<
      T extends Polygon,
      S extends PolygonSerialization,
      P extends PolygonSpecification,
      RULE extends TruncationRule<T, S, P>,
    >() {
      const zoneStore = useZoneStore()

      const parents: Parent[] = []
      for (const zone of Object.values(zoneStore.available)) {
        if (zone.hasRegions) {
          for (const region of zone.regions) {
            parents.push({ zone, region } as Parent)
          }
        } else {
          parents.push({ zone, region: null } as Parent)
        }
      }

      const faciesStore = useFaciesStore()
      const faciesGroupStore = useFaciesGroupStore()
      const truncationRuleStore = useTruncationRuleStore()

      const stores = [truncationRuleStore, faciesGroupStore, faciesStore]

      parents.flatMap((parent) =>
        stores.flatMap((store) =>
          (store.available as (RULE | FaciesGroup | Facies)[])
            .filter((item) => item.isChildOf(parent))
            .flatMap((item) => store.remove(item as any)),
        ),
      )
    }

    async function select(blockedWellLog: string | null = null) {
      if (blockedWellLog === '') {
        console.warn(
          'Setting blocked well log to an empty string; using null instead',
        )
        blockedWellLog = null
      }

      selected.value = blockedWellLog
      _removeFaciesDependent()

      const faciesGlobalStore = useGlobalFaciesStore()
      const faciesStore = useFaciesStore()
      if (blockedWellLog) {
        await faciesGlobalStore.fetch()
        faciesStore.selectObserved()
      } else {
        faciesGlobalStore.$reset()
      }
    }

    async function fetch() {
      selected.value = null
      await refresh()
      const selection = available.value.length === 1 ? available.value[0] : null
      await select(selection)
    }

    async function refresh() {
      loading.value = true
      const gridModelStore = useGridModelStore()
      const gridModel = gridModelStore.current
      const parameterBlockedWellStore = useParameterBlockedWellStore()
      const blockedWell = parameterBlockedWellStore.selected
      try {
        available.value =
          gridModel && blockedWell
            ? await rms.blockedWellLogParameters(gridModel.name, blockedWell)
            : []
      } finally {
        loading.value = false
      }
    }

    return {
      available,
      selected,
      select,
      fetch,
      refresh,
      $reset,
      loading,
    }
  },
)

if (import.meta.hot) {
  import.meta.hot.accept(
    acceptHMRUpdate(useParameterBlockedWellLogStore, import.meta.hot),
  )
}
