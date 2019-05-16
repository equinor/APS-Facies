<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
    :custom-sort="ordering"
    item-key="id"
    class="elevation-0"
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
          <alpha-selection
            :value="props.item.field"
            :rule="rule"
            :group="props.item.group.id"
            hide-label
            @input="field => updateField(props.item, field)"
          />
        </td>
        <td>
          <overlay-facies-specification
            :value="props.item"
            :rule="rule"
          />
        </td>
        <td v-if="needFraction">
          <fraction-field
            :value="props.item.fraction"
            :disabled="!multipleFaciesSpecified(props.item)"
            @input="val => updateFraction(props.item, val)"
          />
        </td>
        <td>
          <fraction-field
            :value="props.item.center"
            @input="val => updateCenter(props.item, val)"
          />
        </td>
        <td>
          <polygon-order
            :value="props.item"
            overlay
          />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Vue, Component, Prop } from 'vue-property-decorator'

import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import FractionField from '@/components/selection/FractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import PolygonOrder from '@/components/specification/TruncationRule/order.vue'
import OverlayFaciesSpecification from '@/components/specification/Facies/overlay.vue'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection.vue'
import Polygon from '@/utils/domain/polygon/base'

import { Facies } from '@/utils/domain'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import { ID } from '@/utils/domain/types'
import { Store } from '@/store/typing'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { sortByOrder } from '@/utils'

@Component({
  components: {
    AlphaSelection,
    OverlayFaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
  },
})
export default class OverlayTable extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayPolygon[]

  @Prop({ required: true })
  readonly rule!: OverlayTruncationRule<Polygon>

  get polygons () {
    // TODO: Include 'help' messages
    return this.value
  }
  get fieldOptions () {
    return Object.values((this.$store as Store).getters.fields)
      .map(field => {
        return {
          value: field.id,
          text: field.name,
          disabled: false,
        }
      })
  }
  get needFraction () {
    return hasFaciesSpecifiedForMultiplePolygons(this.rule.overlayPolygons)
  }
  get headers () {
    return [
      {
        text: 'GRF',
        align: 'left',
        sortable: false,
        value: 'field',
        help: 'Gaussian Random Field',
      },
      {
        text: 'Overlay Facies',
        align: 'left',
        sortable: false,
        value: 'facies',
        help: '',
      },
      ...(this.needFraction
        ? [{
          text: 'Probability Fraction',
          align: 'left',
          sortable: false,
          value: 'fraction',
          help: '',
        }]
        : []),
      {
        text: 'Center',
        align: 'left',
        sortable: false,
        value: 'center',
        help: 'Truncation Interval Center Point',
        /* or: The overlay facies will look more continuous if the value of the center point of
               the truncation interval is 0 or 1 and look more fragmented if a value between 0 and 1,
               typically 0.5 is chosen. */
      },
      {
        text: 'Order',
        align: 'left',
        sortable: false,
        value: 'order',
        help: '',
      }
    ]
  }

  ordering (items: OverlayPolygon[], index: number, isDescending: boolean) { return sortByOrder(items, index, isDescending) }
  async updateField (polygon: OverlayPolygon, fieldId: ID) {
    const field = (this.$store as Store).state.gaussianRandomFields.fields[`${fieldId}`]
    await this.$store.dispatch('truncationRules/updateOverlayField', { rule: this.rule, polygon, field })
  }
  async updateFraction (polygon: OverlayPolygon, val: number) {
    await this.$store.dispatch('truncationRules/updateOverlayFraction', { rule: this.rule, polygon, value: val })
  }
  async updateCenter (polygon: OverlayPolygon, val: number) {
    await this.$store.dispatch('truncationRules/updateOverlayCenter', { rule: this.rule, polygon, value: val })
  }
  multipleFaciesSpecified ({ facies }: Facies) {
    return hasFaciesSpecifiedForMultiplePolygons(this.rule.overlayPolygons, facies)
  }
}
</script>

<style scoped>
th {
  white-space: normal;
  overflow-wrap: break-spaces;
}
</style>
