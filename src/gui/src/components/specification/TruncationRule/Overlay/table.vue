<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
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
          <background-facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <alpha-selection
            :value="props.item.field"
            :channel="channel(props.item.order)"
            hide-label
            @input="field => updateField(props.item, field)"
          />
        </td>
        <td>
          <facies-specification
            :value="props.item"
            :rule="value"
            @input="val => updateFacies(props.item, val)"
          />
        </td>
        <td>
          <fraction-field
            :value="props.item.fraction"
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
          />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import { mapGetters } from 'vuex'
import VueTypes from 'vue-types'

import FractionField from '@/components/selection/FractionField'
import NumericField from '@/components/selection/NumericField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import IconButton from '@/components/selection/IconButton'
import PolygonOrder from '@/components/specification/TruncationRule/order'
import FaciesSpecification from '@/components/specification/Facies'
import BackgroundFaciesSpecification from '@/components/specification/Facies/background'
import AlphaSelection from '@/components/specification/TruncationRule/AlphaSelection'

import { updateFacies } from '@/store/utils'
import { TruncationRule } from '@/store/utils/domain'

export default {
  components: {
    AlphaSelection,
    BackgroundFaciesSpecification,
    FaciesSpecification,
    PolygonOrder,
    IconButton,
    OptionalHelpItem,
    FractionField,
    NumericField,
  },

  props: {
    value: VueTypes.instanceOf(TruncationRule).isRequired,
  },

  computed: {
    ...mapGetters({
      selectedFacies: 'facies/selected',
    }),
    polygons () {
      // TODO: Include 'help' messages
      return this.value
        ? this.value.overlayPolygons
        : []
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
    headers () {
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
        {
          text: 'Probability Fraction',
          align: 'left',
          sortable: false,
          value: 'fraction',
          help: '',
        },
        {
          text: 'Truncation Interval Center Point',
          align: 'left',
          sortable: false,
          value: 'center',
          help: '',
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
    updateField (item, fieldId) {
      this.$store.dispatch('truncationRules/updateFields', { rule: this.value, channel: this.channel(item), selected: fieldId })
    },
    updateFacies (item, faciesId) {
      updateFacies(this.$store.dispatch, this.value, item, faciesId, false)
    },
    updateFraction (item, val) {
      this.$store.dispatch('truncationRules/updateOverlayFraction', { rule: this.value, polygon: item, value: val })
    },
    updateCenter (item, val) {
      this.$store.dispatch('truncationRules/updateOverlayCenter', { rule: this.value, polygon: item, value: val })
    },
    channel (order) {
      order = order.order || order
      // +1 due to order being 0-indexed, but `channel` is expected to be 1-indexed
      return order + 1 + this.value.fields.filter(({ overlay }) => !overlay).length
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
