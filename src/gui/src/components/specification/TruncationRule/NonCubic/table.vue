<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
    :custom-sort="order"
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
          <optional-help-item
            :value="props.item.name"
          />
        </td>
        <td class="text-xs-left">
          <numeric-field
            :value="props.item.angle"
            :ranges="{min: -180.0, max: 180.0}"
            enforce-ranges
            allow-negative
            use-modulus
            unit="°"
            label=""
            @input="angle => updateAngle(props.item, angle)"
          />
        </td>
        <td class="text-xs-left">
          <facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td
          v-if="hasMultipleFaciesSpecified"
        >
          <fraction-field
            :value="props.item.fraction"
            :disabled="!multipleFaciesSpecified(props.item)"
            @input="fraction => updateFactor(props.item, fraction)"
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
import { AppTypes } from '@/utils/typing'

import FractionField from '@/components/selection/FractionField'
import NumericField from '@/components/selection/NumericField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import PolygonOrder from '@/components/specification/TruncationRule/order'
import FaciesSpecification from '@/components/specification/Facies'

import { notEmpty } from '@/utils'

export default {
  components: {
    FaciesSpecification,
    PolygonOrder,
    OptionalHelpItem,
    FractionField,
    NumericField,
  },

  props: {
    value: AppTypes.truncationRule,
  },

  computed: {
    polygons () {
      // TODO: Include 'help' messages
      return !this.value
        ? []
        : this.value.backgroundPolygons
          .map(polygon => {
            const settings = this.value.settings[polygon.id]
            return {
              ...polygon,
              ...settings,
            }
          })
    },
    headers () {
      return [
        {
          text: 'Polygon',
          align: 'left',
          sortable: false,
          value: 'name',
          help: '',
        },
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
            text: 'Proportion Factor',
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
    },
    hasMultipleFaciesSpecified () {
      return this.value
        ? Object.values(this.value.polygons)
          .some(polygon => (
            notEmpty(polygon.facies) &&
            this.multipleFaciesSpecified(polygon)
          ))
        : false
    }
  },

  methods: {
    order (items, index, isDescending) {
      return items.slice().sort((polygon, other) => polygon.order - other.order)
    },
    updateFactor (item, value) {
      return this.$store.dispatch('truncationRules/changeProportionFactors', { rule: this.value, polygon: item, value })
    },
    updateAngle (item, value) {
      return this.$store.dispatch('truncationRules/changeAngles', { rule: this.value, polygon: item, value })
    },
    multipleFaciesSpecified (item) {
      return Object.values(this.value.polygons)
        .filter(polygon => polygon.facies === item.facies).length > 1
    },
  },
}
</script>
