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
            :channel="channel(props.item.order)"
            :rule="rule"
            :group="props.item.group"
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

<script>
import FractionField from '@/components/selection/FractionField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import PolygonOrder from '@/components/specification/TruncationRule/order'
import FaciesSpecification from '@/components/specification/Facies'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection'

import { updateFacies } from '@/store/utils'
import { hasFaciesSpecifiedForMultiplePolygons, sortByOrder } from '@/utils'
import { AppTypes } from '@/utils/typing'
import VueTypes from 'vue-types'

export default {
  components: {
    AlphaSelection,
    FaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
  },

  props: {
    value: VueTypes.arrayOf(VueTypes.any).isRequired,
    rule: AppTypes.truncationRule.isRequired,
  },

  computed: {
    polygons () {
      // TODO: Include 'help' messages
      return this.value
    },
    fieldOptions () {
      return Object.values(this.$store.getters.fields)
        .map(field => {
          return {
            value: field.id,
            text: field.name,
            disabled: false,
          }
        })
    },
    needFraction () {
      return hasFaciesSpecifiedForMultiplePolygons(this.rule.overlayPolygons)
    },
    headers () {
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
    },
  },

  methods: {
    backgroundFacies (facies) {
      const backgroundFacies = [...new Set(this.rule.backgroundPolygons.map(({ facies }) => facies))]
      return backgroundFacies.indexOf(facies.id) >= 0
    },
    ordering (...args) { return sortByOrder(...args) },
    updateField (item, fieldId) {
      this.$store.dispatch('truncationRules/updateFields', { rule: this.rule, channel: this.channel(item), selected: fieldId })
    },
    updateFacies (item, faciesId) {
      updateFacies(this.$store.dispatch, this.rule, item, faciesId, false)
    },
    updateFraction (item, val) {
      this.$store.dispatch('truncationRules/updateOverlayFraction', { rule: this.rule, polygon: item, value: val })
    },
    updateCenter (item, val) {
      this.$store.dispatch('truncationRules/updateOverlayCenter', { rule: this.rule, polygon: item, value: val })
    },
    channel (order) {
      order = order.hasOwnProperty('order') ? order.order : order
      // +1 due to order being 0-indexed, but `channel` is expected to be 1-indexed
      return order + 1 + this.rule.fields.filter(({ overlay }) => !overlay).length
    },
    multipleFaciesSpecified ({ facies }) {
      return hasFaciesSpecifiedForMultiplePolygons(this.rule.overlayPolygons, facies)
    },
  },
}
</script>

<style scoped>
th {
  white-space: normal;
  overflow-wrap: break-spaces;
}
</style>
