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
          <facies-specification
            :value="props.item"
            :rule="rule"
            :disable="facies => backgroundFacies(facies)"
            @input="val => updateFacies(props.item, val)"
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
import { Facies, GaussianRandomField } from '@/utils/domain'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import { ID } from '@/utils/domain/types'
import { Vue, Component, Prop } from 'vue-property-decorator'

import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

import FractionField from '@/components/selection/FractionField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import PolygonOrder from '@/components/specification/TruncationRule/order'
import FaciesSpecification from '@/components/specification/Facies'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection'

import { updateFacies } from '@/store/utils'
import { hasFaciesSpecifiedForMultiplePolygons, sortByOrder } from '@/utils'
import Polygon from '@/utils/domain/polygon/base'

interface Ordered {
  order: number
  [_: string]: any
}

type Order = number | Ordered

@Component({
  components: {
    AlphaSelection,
    FaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
  },
})
export default class OverlayTable extends Vue {
  @Prop({ required: true })
  value: OverlayPolygon[]
  @Prop({ required: true })
  rule: OverlayTruncationRule<Polygon>

  get polygons () {
    // TODO: Include 'help' messages
    return this.value
  }
  get fieldOptions () {
    return (Object.values(this.$store.getters.fields) as GaussianRandomField[]) // TODO: Type annotate store
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

  backgroundFacies (facies: Facies) {
    return this.rule.isUsedInBackground(facies)
  }
  ordering (...args: OverlayPolygon[]) { return sortByOrder(...args) }
  updateField (item: OverlayPolygon, fieldId: ID) {
    this.$store.dispatch('truncationRules/updateFields', { rule: this.rule, channel: this.channel(item), selected: fieldId })
  }
  updateFacies (item: OverlayPolygon, faciesId: ID) {
    updateFacies(this.$store.dispatch, this.rule, item, faciesId, false)
  }
  updateFraction (item: OverlayPolygon, val: number) {
    this.$store.dispatch('truncationRules/updateOverlayFraction', { rule: this.rule, polygon: item, value: val })
  }
  updateCenter (item: OverlayPolygon, val: number) {
    this.$store.dispatch('truncationRules/updateOverlayCenter', { rule: this.rule, polygon: item, value: val })
  }
  // channel (order: Order) {
  //   order = order.hasOwnProperty('order') ? (order as Ordered).order : order
  //   // +1 due to order being 0-indexed, but `channel` is expected to be 1-indexed
  //   return (order as number) + 1 + this.rule.fields.filter(({ overlay }) => !overlay).length
  // }
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
