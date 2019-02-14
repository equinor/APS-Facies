<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
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
            :value="props.item"
          />
        </td>
        <td class="text-xs-left">
          <!--TODO: Figure out why input happens twice-->
          <facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <fraction-field
            v-if="!!props.item.factor"
            :value="props.item.factor"
            fmu-updatable
            @input="factor => updateFactor(props.item, factor)"
          />
          <slot v-else />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import { isNumber } from 'lodash'
import { mapGetters } from 'vuex'

import FractionField from '@/components/selection/FractionField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import FaciesSpecification from '@/components/specification/Facies'

import { updateFacies } from '@/store/utils'
import { AppTypes } from '@/utils/typing'

export default {
  components: {
    OptionalHelpItem,
    FractionField,
    FaciesSpecification,
  },

  props: {
    value: AppTypes.truncationRule,
  },

  computed: {
    ...mapGetters({
      selectedFacies: 'facies/selected',
    }),
    polygons () {
      // TODO: Include 'help' messages
      return !this.value
        ? []
        : this.value.backgroundPolygons
          .map(polygon => {
            const factor = isNumber(polygon.factor) ? polygon.factor : null
            const options = {
              ...polygon,
              hasFactor: !!factor,
            }
            if (factor) options['factor'] = factor
            return options
          })
    },
    faciesOptions () {
      return this.selectedFacies.map(facies => {
        return {
          text: facies.name,
          value: facies.id,
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
          text: 'Facies',
          align: 'left',
          sortable: false,
          value: 'facies',
          help: '',
        },
        {
          text: 'Slant Factor',
          align: 'left',
          sortable: false,
          value: 'factor',
          help: '',
        }
      ]
    }
  },

  methods: {
    updateFacies (item, faciesId) {
      updateFacies(this.$store.dispatch, this.value, item, faciesId)
    },
    updateFactor (item, value) {
      return this.$store.dispatch('truncationRules/changeSlantFactors', {
        rule: this.value,
        polygon: item,
        value
      })
    },
  },
}
</script>
