<template>
  <base-table
    :headers="headers"
    :items="groups"
    :no-data-text="noDataText"
    item-key="id"
    @input.stop
  >
    <template
      v-slot:item="{ item }"
    >
      <tr>
        <td>
          <background-group-facies-specification
            :value="item"
            :rule="value"
          />
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

<script lang="ts">
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import { Component, Prop, Vue } from 'vue-property-decorator'

import Facies from '@/utils/domain/facies/local'
import { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import { Polygon } from '@/utils/domain'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import BackgroundGroupFaciesSpecification from '@/components/specification/Facies/backgroundGroup.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import PolygonTable from './table.vue'

function hasAvailableBackgroundFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> (store: Store, rule: OverlayTruncationRule<T, S, P>): boolean {
  return Object.values(store.state.facies.available)
    .some(facies => store.getters['facies/availableForBackgroundFacies'](rule, facies))
}

function allBackgroundPolygonsHasSomeFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> (rule: OverlayTruncationRule<T, S, P>): boolean {
  return rule.overlayPolygons
    .every(({ group }) => group ? group.facies.length > 0 : true)
}

@Component({
  components: {
    BaseTable,
    OptionalHelpItem,
    BackgroundGroupFaciesSpecification,
    PolygonTable,
  },
})
export default class BackgroundFacies<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayTruncationRule<T, S, P>

  get groups () {
    let overlay: { group: ID, polygons: Facies[] }[] = []
    if (this.value) {
      const groups = {}
      const polygons = this.value.overlayPolygons
      polygons.forEach((polygon): void => {
        if (!groups.hasOwnProperty(polygon.group.id)) groups[polygon.group.id] = []
        groups[polygon.group.id].push(polygon)
      })
      overlay = Object.keys(groups).map(groupId => { return { group: groupId, polygons: groups[`${groupId}`] } })
    }
    if (
      hasAvailableBackgroundFacies(this.$store, this.value)
      && allBackgroundPolygonsHasSomeFacies(this.value)
    ) {
      overlay.push({ group: '', polygons: [] })
    }
    return overlay
  }

  get headers () {
    return [
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
  }

  get noDataText (): string {
    if (this.value.polygons.every(polygon => !polygon.facies)) {
      return 'No background facies are given'
    } else {
      return '$vuetify.noDataText'
    }
  }
}
</script>
