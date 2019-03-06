<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :no-data-text="noDataText"
    item-key="name"
    class="elevation-1"
    hide-actions
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
        <td>
          {{ props.item.name }}
        </td>
        <td
          v-if="useProbabilityCubes"
        >
          <v-autocomplete
            :value="props.item.probabilityCube"
            :items="probabilityCubes"
            clearable
            @input="cube => changeProbabilityCube(props.item, cube)"
          />
        </td>
        <td
          v-if="useProbabilityCubes"
        >
          {{ props.item.previewProbability }}
        </td>
        <td
          v-else
        >
          <fraction-field
            :value="props.item.previewProbability"
            label=""
            @input="prob => changeProbability(props.item, prob)"
          />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import { mapState } from 'vuex'

import FractionField from '@/components/selection/FractionField'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import { hasCurrentParents } from '@/utils'

export default {
  components: {
    OptionalHelpItem,
    FractionField,
  },

  computed: {
    ...mapState({
      probabilityCubes: state => [{ text: '', disabled: false }]
        .concat(state.parameters.probabilityCube.available
          .map(parameter => {
            return {
              text: parameter,
              disabled: Object.values(state.facies.available)
                .map(facies => facies.probabilityCube).indexOf(parameter) >= 0
            }
          })
        ),
    }),
    useProbabilityCubes () {
      return !this.$store.getters['facies/constantProbability']()
    },
    items () {
      const state = this.$store.state
      const getters = this.$store.getters
      const items = state.facies.available
      return Object.values(items)
        .filter(item => hasCurrentParents(item, getters))
        .map(item => {
          return {
            id: item.id,
            name: getters['facies/name'](item.facies),
            ...item,
          }
        })
    },
    noDataText () {
      return 'No Facies selected'
    },
    headers () {
      const headers = [
        {
          text: 'Facies',
          align: 'left',
          sortable: false,
          value: 'name',
        },
        {
          text: 'Probability Cube',
          align: 'left',
          sortable: false,
          value: 'probabilityCube',
        },
        {
          text: this.useProbabilityCubes ? 'Preview Probability' : 'Probability',
          align: 'left',
          sortable: false,
          value: 'previewProbability',
        },
      ]
      return headers
        .filter(item => this.useProbabilityCubes
          ? true
          : item.value !== 'probabilityCube'
        )
    },
  },

  methods: {
    changeProbabilityCube (facies, probabilityCube) {
      this.$store.dispatch('facies/changed', { id: facies.id, probabilityCube })
    },
    changeProbability (facies, prob) {
      this.$store.dispatch('facies/changed', { id: facies.id, previewProbability: prob })
    },
  },

}
</script>
