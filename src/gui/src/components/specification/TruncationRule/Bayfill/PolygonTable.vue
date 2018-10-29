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
      <v-tooltip bottom>
        <span slot="activator">
          {{ props.header.text }}
        </span>
        <span>
          {{ props.header.help }}
        </span>
      </v-tooltip>
    </template>
    <template
      slot="items"
      slot-scope="props"
    >
      <tr>
        <td class="text-xs-left">
          <v-tooltip
            v-if="!!props.item.help"
            bottom
          >
            <span slot="activator">
              {{ props.item.name }}
            </span>
            <span>
              {{ props.item.help }}
            </span>
          </v-tooltip>
          <span v-else>{{ props.item.name }}</span>
        </td>
        <td class="text-xs-left">
          <!--TODO: Figure out why input happens twice-->
          <v-select
            :items="faciesOptions"
            :value="props.item.facies"
            @input.capture="facies => updateFacies(props.item, facies)"
          />
        </td>
        <td>
          <fraction-field
            v-if="!!props.item.factor"
            :value="props.item.factor"
            fmu-updatable
            @input="value => updateFactor(props.item, value)"
          />
          <slot v-else/>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import { mapGetters } from 'vuex'

import FractionField from '@/components/selection/FractionField'
import { notEmpty } from '@/utils'

export default {
  components: {
    FractionField,
  },

  computed: {
    ...mapGetters({
      selectedFacies: 'facies/selected',
      truncationRule: 'truncationRule',
    }),
    polygons () {
      // TODO: Include 'help' messages
      return !this.truncationRule
        ? []
        : Object.values(this.truncationRule.polygons).map(polygon => {
          let factor = null
          const setting = this.truncationRule.settings[polygon.id]
          if (notEmpty(setting)) {
            factor = setting.factor
          }
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
    updateFacies (polygon, faciesId) {
      const existing = Object.values(this.truncationRule.polygons)
        .find(polygon => polygon.facies === faciesId)
      return existing
        ? this.$store.dispatch('truncationRules/swapFacies', {
          rule: this.truncationRule,
          polygons: [polygon, existing]
        })
        : this.$store.dispatch('truncationRules/updateFacies', {
          rule: this.truncationRule,
          polygon,
          faciesId
        })
    },
    updateFactor (item, value) {
      return this.$store.dispatch('truncationRules/changeFactors', {
        polygon: item,
        value
      })
    },
  },
}
</script>

<style scoped>

</style>
