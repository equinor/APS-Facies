<template>
  <v-data-table
    :headers="headers"
    :items="groups"
    item-key="id"
    class="elevation-1"
    hide-actions
    @input.stop
  >
    <template
      slot="header-cell"
      slot-scope="props"
      class="text-xs-left"
    >
      <optional-help-item
        :value="props.header"
      />
    </template>
    <template
      slot="items"
      slot-scope="props"
    >
      <tr>
        <td>
          <background-group-facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <polygon-table
            v-if="props.item.polygons.length > 0"
            :value="props.item.polygons"
            :rule="value"
          />
          <span v-else>
            {{ 'Select one, or more background facies' }}
          </span>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import Facies from '@/utils/domain/facies/local'
import { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Polygon } from '@/utils/domain'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import BackgroundGroupFaciesSpecification from '@/components/specification/Facies/backgroundGroup.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import PolygonTable from './table.vue'

function hasAvailableBackgroundFacies<T extends Polygon> (store: Store, rule: OverlayTruncationRule<T>): boolean {
  return Object.values(store.state.facies.available)
    .some(facies => store.getters['facies/availableForBackgroundFacies'](rule, facies))
}

function allBackgroundPolygonsHasSomeFacies<T extends Polygon> (rule: OverlayTruncationRule<T>): boolean {
  return rule.overlayPolygons
    .every(({ group }) => group ? group.facies.length > 0 : true)
}

@Component({
  components: {
    OptionalHelpItem,
    BackgroundGroupFaciesSpecification,
    PolygonTable,
  },
})
export default class BackgroundFacies<T extends Polygon> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayTruncationRule<T>

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
        align: 'left',
        sortable: false,
        value: 'group',
        class: 'text-wrap-newline',
        help: 'Which facies this overlay polygon should cover',
      },
      {
        text: 'Polygons',
        align: 'left',
        sortable: false,
        value: 'polygon',
        help: 'Specification of the polygons',
      },
    ]
  }
}
</script>
