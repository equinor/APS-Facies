<template>
  <base-table
    :headers="headers"
    :items="idGroups"
    :no-data-text="noDataText"
    item-key="id"
    @input.stop
  >
    <template #item="{ item }">
      <tr>
        <td>
          <background-group-facies-specification :value="item" :rule="value as RULE" />
        </td>
        <td>
          <polygon-table
            v-if="item.polygons.length > 0"
            :value="item.polygons"
            :rule="value as OverlayTruncationRule<T, S, P>"
          />
          <span v-else>Select one, or more background facies </span>
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script
  setup
  lang="ts"
  generic="T extends OverlayPolygon,
  S extends PolygonSerialization,
  P extends PolygonSpecification,
  RULE extends OverlayTruncationRule<T, S, P> | InstantiatedOverlayTruncationRule
"
>
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import type { HeaderItems } from '@/utils/typing'
import type {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import type { ID } from '@/utils/domain/types'
import type { Facies, InstantiatedOverlayTruncationRule, OverlayPolygon } from '@/utils/domain'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import BackgroundGroupFaciesSpecification from '@/components/specification/Facies/backgroundGroup.vue'
import PolygonTable from './table.vue'

import { hasOwnProperty } from '@/utils/helpers'
import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'

function hasAvailableBackgroundFacies(
  rule: RULE,
): boolean {
  const faciesStore = useFaciesStore()
  return faciesStore.available.some((facies) =>
    faciesStore.availableForBackgroundFacies(rule, facies as Facies),
  )
}

function allBackgroundPolygonsHasSomeFacies(
  rule: RULE,
): boolean {
  return rule.overlayPolygons.every(({ group }) =>
    group ? group.facies.length > 0 : true,
  )
}

const props = defineProps<{ value: RULE }>()

const groups = computed(() => {
  let overlay: { group: ID; polygons: OverlayPolygon[] }[] = []
  if (props.value) {
    const groupRecord: Record<ID, OverlayPolygon[]> = {}
    const polygons = props.value.overlayPolygons
    polygons.forEach((polygon): void => {
      if (!hasOwnProperty(groupRecord, polygon.group.id))
        groupRecord[polygon.group.id] = []
      groupRecord[polygon.group.id].push(polygon)
    })
    overlay = Object.keys(groupRecord).map((groupId) => {
      return { group: groupId, polygons: groupRecord[groupId] }
    })
  }
  if (
    hasAvailableBackgroundFacies(props.value) &&
    allBackgroundPolygonsHasSomeFacies(props.value)
  ) {
    overlay.push({ group: '', polygons: [] })
  }
  return overlay
})

type Item = {id: ID, polygons: Array<OverlayPolygon>}

const idGroups = computed((): Array<Item> =>
  groups.value.map(({ group, polygons }) => ({ id: group, polygons })),
)

const headers: HeaderItems = [
  {
    text: 'Background',
    value: 'group',
    class: 'text-wrap-newline',
    help: 'Which facies this overlay polygon should cover',
  },
  {
    text: 'Polygons',
    value: 'polygon',
    help: 'Specification of the polygons',
  },
]

const noDataText = computed(() =>
  props.value.polygons.every((polygon) => !polygon.facies)
    ? 'No background facies are given'
    : '$vuetify.noDataText',
)
</script>
