<template>
  <v-container
    class="text-center column wrap align"
  >
    <v-row>
      <v-col cols="12">
        <v-select
          v-model="selected"
          :items="available"
          label="Gaussian Fields to be used"
          multiple
        />
      </v-col>
    </v-row>
    <v-row
      align="center"
      justify="space-around"
    >
      <v-col
        v-for="([field, other], index) in combinations"
        :key="index"
      >
        <cross-plot
          v-if="field.simulated && other.simulated "
          :value="[field, other]"
        />
        <v-progress-circular
          v-else
          :size="70"
          indeterminate
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import { ID } from '@/utils/domain/types'

import CrossPlot from './index.vue'

interface Item {
  value: ID
  text: string
}

@Component({
  components: {
    CrossPlot,
  },
})
export default class CrossPlots extends Vue {
  @Prop({ required: true })
  value: GaussianRandomField[]

  selected: ID[] = []

  get available (): Item[] {
    return this.value.map(field => {
      return {
        value: field.id,
        text: field.name,
      }
    })
  }

  get combinations (): number[][] {
    const pairs: number[][] = []
    const available = this.selected
      .map(id => this.$store.state.gaussianRandomFields.available[`${id}`])
    if (!available) return pairs
    for (let i = 0; i < available.length; i++) {
      for (let j = i + 1; j < available.length; j++) {
        pairs.push([available[`${i}`], available[`${j}`]])
      }
    }
    return pairs
  }

  @Watch('selected', { deep: true })
  selectionChanged (fields: ID[]): void {
    this.$store.dispatch('gaussianRandomFields/updateSimulations', { fields })
  }

  @Watch('available', { deep: true })
  onChange (value: Item[]): void {
    if (this.selected.some(selectedItem => !value.find(availableItem => availableItem.value === selectedItem))) {
      // That is, if there is some selected value that is no longer available
      this.selected = this.available
        .filter(availableItem => this.selected.some(selectedItem => selectedItem === availableItem.value))
        .map(el => el.value)
    }
  }

  beforeMount (): void {
    if (this.selected.length === 0 && this.value.length >= 2) {
      this.value.slice(0, 2).forEach(field => this.selected.push(field.id))
    }
  }
}
</script>
