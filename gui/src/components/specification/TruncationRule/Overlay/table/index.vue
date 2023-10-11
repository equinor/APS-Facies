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
            :rule="value"
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
  generic="
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
"
>
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import { HeaderItems } from '@/utils/typing'
import Facies from '@/utils/domain/facies/local'
import {
  PolygonSerialization,
  PolygonSpecification,
} from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import { Polygon } from '@/utils/domain'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import BackgroundGroupFaciesSpecification from '@/components/specification/Facies/backgroundGroup.vue'
import PolygonTable from './table.vue'

import { hasOwnProperty } from '@/utils/helpers'
import { computed } from 'vue'
import { useStore } from '../../../../../store'

function hasAvailableBackgroundFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
>(store: Store, rule: OverlayTruncationRule<T, S, P>): boolean {
  return Object.values(store.state.facies.available).some((facies) =>
    store.getters['facies/availableForBackgroundFacies'](rule, facies),
  )
}

function allBackgroundPolygonsHasSomeFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
>(rule: OverlayTruncationRule<T, S, P>): boolean {
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
