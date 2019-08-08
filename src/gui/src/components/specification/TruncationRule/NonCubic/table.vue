<template>
  <base-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
    @input.stop
  >
    <template
      v-slot:item="{ item }"
    >
      <tr>
        <td class="text-left">
          <numeric-field
            :value="item.angle"
            :ranges="{min: -180.0, max: 180.0}"
            :disabled="isLast(item)"
            fmu-updatable
            enforce-ranges
            allow-negative
            use-modulus
            unit="°"
            label=""
            @input="angle => updateAngle(item, angle)"
          />
        </td>
        <td class="text-left">
          <background-facies-specification
            :value="item"
            :rule="value"
          />
        </td>
        <td
          v-if="hasMultipleFaciesSpecified"
        >
          <polygon-fraction-field
            :value="item"
            :rule="value"
          />
        </td>
        <td>
          <polygon-order
            :value="item"
            :rule="value"
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script lang="ts">
import BaseTable from '@/components/baseComponents/BaseTable.vue'
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
    BaseTable,
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
        value: 'angle',
      },
      {
        text: 'Facies',
        value: 'facies',
      },
      ...(this.hasMultipleFaciesSpecified ? [
        {
          text: 'Probability Fraction',
          value: 'fraction',
          help: 'The fraction of the facies probability assigned to the individual polygon',
        },
      ] : []),
      {
        text: 'Order',
        value: 'order',
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

  isLast (polygon: NonCubicPolygon): boolean {
    return this.polygons.findIndex(({ id }) => id === polygon.id) === (this.polygons.length - 1)
  }
}
</script>
