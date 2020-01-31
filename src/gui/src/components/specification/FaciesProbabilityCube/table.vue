<template>
  <base-table
    :headers="headers"
    :items="items"
    :no-data-text="noDataText"
    elevation="0"
  >
    <template
      v-slot:item="{ item }"
    >
      <tr>
        <td>
          {{ item.name }}
        </td>
        <td
          v-if="useProbabilityCubes"
        >
          <v-autocomplete
            :value="item.probabilityCube"
            :items="probabilityCubes"
            clearable
            @input="cube => changeProbabilityCube(item, cube)"
          />
        </td>
        <td
          v-if="useProbabilityCubes"
        >
          {{ item.previewProbability }}
        </td>
        <td
          v-else
        >
          <fraction-field
            :value="item.previewProbability"
            label=""
            dense
            @input="prob => changeProbability(item, prob)"
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import Facies, { ProbabilityCube } from '@/utils/domain/facies/local'
import { Store } from '@/store/typing'
import { HeaderItems, ListItem } from '@/utils/typing'

import { hasCurrentParents } from '@/utils'

@Component({
  components: {
    BaseTable,
    OptionalHelpItem,
    FractionField,
  },
})
export default class FaciesProbabilityCubeTable extends Vue {
  get facies (): Facies[] {
    return (Object.values(this.$store.state.facies.available) as Facies[])
      .filter(facies => hasCurrentParents(facies, this.$store.getters))
  }

  get probabilityCubes (): ListItem<ProbabilityCube>[] {
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

  get useProbabilityCubes (): boolean {
    return !(this.$store as Store).getters['facies/constantProbability']()
  }

  get items (): Facies[] {
    return this.facies
      .sort((a, b) => a.code - b.code)
  }

  get noDataText (): string {
    return 'No Facies selected'
  }

  get headers (): HeaderItems {
    const headers = [
      {
        text: 'Facies',
        value: 'name',
      },
      {
        text: 'Probability Cube',
        value: 'probabilityCube',
      },
      {
        text: this.useProbabilityCubes ? 'Preview Probability' : 'Probability',
        value: 'previewProbability',
      },
    ]
    return headers
      .filter(item => this.useProbabilityCubes
        ? true
        : item.value !== 'probabilityCube'
      )
  }

  changeProbabilityCube (facies: Facies, probabilityCube: string): void {
    this.$store.dispatch('facies/changeProbabilityCube', { facies, probabilityCube })
  }

  changeProbability (facies: Facies, prob: number): void {
    this.$store.dispatch('facies/changePreviewProbability', { facies, previewProbability: prob })
  }
}
</script>
