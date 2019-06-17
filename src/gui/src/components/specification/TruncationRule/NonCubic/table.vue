<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
    item-key="name"
    class="elevation-1"
    hide-actions
    @input.stop
  >
    <template
      slot="headerCell"
      slot-scope="props"
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
        <td class="text-xs-left">
          <numeric-field
            :value="props.item.angle"
            :ranges="{min: -180.0, max: 180.0}"
            fmu-updatable
            enforce-ranges
            allow-negative
            use-modulus
            unit="°"
            label=""
            @input="angle => updateAngle(props.item, angle)"
          />
        </td>
        <td class="text-xs-left">
          <background-facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td
          v-if="hasMultipleFaciesSpecified"
        >
          <polygon-fraction-field
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <polygon-order
            :value="props.item"
            :rule="value"
          />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'
import NumericField from '@/components/selection/NumericField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import BackgroundFaciesSpecification from '@/components/specification/Facies/background.vue'

import NonCubic from '@/utils/domain/truncationRule/nonCubic'
import NonCubicPolygon from '@/utils/domain/polygon/nonCubic'

import { sortByOrder } from '@/utils'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'

@Component({
  components: {
    BackgroundFaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
    PolygonFractionField,
    NumericField,
  },
})
export default class NonCubicTable extends Vue {
  @Prop({ required: true })
  readonly value!: NonCubic

  get polygons () {
    // TODO: Include 'help' messages
    return !this.value
      ? []
      : this.value.backgroundPolygons
  }

  get headers () {
    return [
      {
        text: 'Angle',
        align: 'left',
        sortable: false,
        value: 'angle',
        help: '',
      },
      {
        text: 'Facies',
        align: 'left',
        sortable: false,
        value: 'facies',
        help: '',
      },
      ...(this.hasMultipleFaciesSpecified ? [
        {
          text: 'Probability Fraction',
          align: 'left',
          sortable: false,
          value: 'fraction',
          help: 'The fraction of the facies probability assigned to the individual polygon',
        },
      ] : []),
      {
        text: 'Order',
        align: 'left',
        sortable: false,
        value: 'order',
        help: '',
      }
    ]
  }

  get hasMultipleFaciesSpecified () {
    return hasFaciesSpecifiedForMultiplePolygons(this.polygons)
  }

  ordering (items: NonCubicPolygon[], index: number, isDescending: boolean) { return sortByOrder(items, index, isDescending) }

  updateAngle (item: NonCubicPolygon, value: number) {
    return this.$store.dispatch('truncationRules/changeAngles', { rule: this.value, polygon: item, value })
  }
}
</script>
