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

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'

import Facies from '@/utils/domain/facies/local'
import { Store } from '@/store/typing'

import { hasCurrentParents } from '@/utils'

@Component({
  components: {
    OptionalHelpItem,
    FractionField,
  },
})
export default class FaciesProbabilityCubeTable extends Vue {
  get facies (): Facies[] {
    return (Object.values(this.$store.state.facies.available) as Facies[])
      .filter(facies => hasCurrentParents(facies, this.$store.getters))
  }

  get probabilityCubes () {
    return [{ text: '', disabled: false }]
      .concat((this.$store as Store).state.parameters.probabilityCube.available
        .map((parameter: string) => {
          return {
            text: parameter,
            disabled: this.facies
              .map(facies => facies.probabilityCube)
              .includes(parameter)
          }
        })
      )
  }

  get useProbabilityCubes () {
    return !(this.$store as Store).getters['facies/constantProbability']()
  }

  get items () {
    return this.facies
      .map(item => {
        return {
          id: item.id,
          name: item.name,
          ...item,
        }
      })
  }

  get noDataText () {
    return 'No Facies selected'
  }

  get headers () {
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
  }

  changeProbabilityCube (facies: Facies, probabilityCube: string) {
    this.$store.dispatch('facies/changeProbabilityCube', { facies, probabilityCube })
  }

  changeProbability (facies: Facies, prob: number) {
    this.$store.dispatch('facies/changePreviewProbability', { facies, previewProbability: prob })
  }
}
</script>
