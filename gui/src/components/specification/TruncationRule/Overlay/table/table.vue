<template>
  <base-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
    elevation="0"
    @input.stop
  >
    <template
      #item="{ item }"
    >
      <tr>
        <td>
          <alpha-selection
            :value="item.field"
            :rule="rule"
            :group="item.group.id"
            hide-label
            @input="field => updateField(item, field)"
          />
        </td>
        <td>
          <overlay-facies-specification
            :value="item"
            :rule="rule"
          />
        </td>
        <td v-if="needFraction">
          <polygon-fraction-field
            :value="item"
            :rule="rule"
          />
        </td>
        <td>
          <fraction-field
            :value="item.center"
            @input="val => updateCenter(item, val)"
          />
        </td>
        <td>
          <polygon-order
            :value="item"
            :rule="rule"
            overlay
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import OverlayFaciesSpecification from '@/components/specification/Facies/overlay.vue'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection.vue'
import Polygon, { PolygonSerialization, PolygonSpecification } from '@/utils/domain/polygon/base'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import OverlayPolygon from '@/utils/domain/polygon/overlay'
import { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import { HeaderItems } from '@/utils/typing'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { sortByOrder } from '@/utils'

@Component({
  components: {
    BaseTable,
    AlphaSelection,
    OverlayFaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
    PolygonFractionField,
  },
})
export default class OverlayTable<
  T extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
  P extends PolygonSpecification = PolygonSpecification,
> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayPolygon[]

  @Prop({ required: true })
  readonly rule!: OverlayTruncationRule<T, S, P>

  get polygons (): OverlayPolygon[] {
    // TODO: Include 'help' messages
    return this.value
  }

  get fieldOptions (): { value: ID, text: string, disabled: boolean }[] {
    return Object.values((this.$store as Store).getters.fields)
      .map(field => {
        return {
          value: field.id,
          text: field.name,
          disabled: false,
        }
      })
  }

  get needFraction (): boolean {
    return hasFaciesSpecifiedForMultiplePolygons(this.rule.overlayPolygons)
  }

  get headers (): HeaderItems {
    return [
      {
        text: 'GRF',
        value: 'field',
        help: 'Gaussian Random Field',
      },
      {
        text: 'Overlay Facies',
        value: 'facies',
      },
      ...(this.needFraction
        ? [{
          text: 'Probability Fraction',
          value: 'fraction',
        }]
        : []),
      {
        text: 'Center',
        value: 'center',
        help: 'Truncation Interval Center Point',
        /* or: The overlay facies will look more continuous if the value of the center point of
               the truncation interval is 0 or 1 and look more fragmented if a value between 0 and 1,
               typically 0.5 is chosen. */
      },
      {
        text: 'Order',
        value: 'order',
      }
    ]
  }

  ordering (items: OverlayPolygon[], index: number, isDescending: boolean): OverlayPolygon[] { return sortByOrder(items, index, isDescending) }
  async updateField (polygon: OverlayPolygon, fieldId: ID): Promise<void> {
    const field = (this.$store as Store).state.gaussianRandomFields.available[`${fieldId}`]
    await this.$store.dispatch('truncationRules/updateOverlayField', { rule: this.rule, polygon, field })
  }

  async updateCenter (polygon: OverlayPolygon, val: number): Promise<void> {
    await this.$store.dispatch('truncationRules/updateOverlayCenter', { rule: this.rule, polygon, value: val })
  }
}
</script>

<style lang="scss" scoped>
th {
  white-space: normal;
  overflow-wrap: break-spaces;
}
</style>
