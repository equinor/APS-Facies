<template>
  <base-table
    :headers="headers"
    :items="groups"
    :no-data-text="noDataText"
    item-key="id"
    @input.stop
  >
    <template #item="{ item }">
      <tr>
        <td>
          <background-group-facies-specification :value="item" :rule="value" />
        </td>
        <td>
          <polygon-table
            v-if="item.polygons.length > 0"
            :value="item.polygons"
            :rule="value as OverlayTruncationRule<T, S, P>"
          />
          <span v-else>
            {{ 'Select one, or more background facies' }}
          </span>
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
import { Store } from '@/store/typing'
import type { Facies, InstantiatedOverlayTruncationRule, OverlayPolygon } from '@/utils/domain'
import type OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import BackgroundGroupFaciesSpecification from '@/components/specification/Facies/backgroundGroup.vue'
import PolygonTable from './table.vue'

import { hasOwnProperty } from '@/utils/helpers'
import { computed } from 'vue'
import { useStore } from '../../../../../store'

function hasAvailableBackgroundFacies(
  store: Store,
  rule: RULE,
): boolean {
  return Object.values(store.state.facies.available).some((facies) =>
    store.getters['facies/availableForBackgroundFacies'](rule, facies),
  )
}

function allBackgroundPolygonsHasSomeFacies(rule: RULE): boolean {
  return rule.overlayPolygons.every(({ group }) =>
    group ? group.facies.length > 0 : true,
  )
}

const props = defineProps<{ value: OverlayTruncationRule<T, S, P> }>()
const store = useStore()

const groups = computed(() => {
  let overlay: { group: ID; polygons: Facies[] }[] = []
  if (props.value) {
    const groups = {}
    const polygons = props.value.overlayPolygons
    polygons.forEach((polygon): void => {
      if (!hasOwnProperty(groups, polygon.group.id))
        groups[polygon.group.id] = []
      groups[polygon.group.id].push(polygon)
    })
    overlay = Object.keys(groups).map((groupId) => {
      return { group: groupId, polygons: groups[groupId] }
    })
  }
  if (
    hasAvailableBackgroundFacies(store, props.value) &&
    allBackgroundPolygonsHasSomeFacies(props.value)
  ) {
    overlay.push({ group: '', polygons: [] })
  }
  return overlay
})

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
