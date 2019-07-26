<template>
  <v-expansion-panels
    :expanded="expanded"
    accordion
  >
    <section-title>{{ title }}</section-title>
    <v-expansion-panel
      v-if="hasFacies"
    >
      <v-expansion-panel-header>
        <section-title>Probabilities for Facies</section-title>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <facies-probability-cube />
      </v-expansion-panel-content>
    </v-expansion-panel>
    <v-expansion-panel
      v-if="hasFacies"
    >
      <v-expansion-panel-header>
        <section-title>Truncation Rule</section-title>
      </v-expansion-panel-header>
      <v-expansion-panel-content>
        <truncation-rule />
      </v-expansion-panel-content>
    </v-expansion-panel>
    <gaussian-random-fields />
  </v-expansion-panels>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple.vue'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube/index.vue'
import TruncationRule from '@/components/specification/TruncationRule/index.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { isEmpty } from '@/utils'

@Component({
  components: {
    IconButton,
    SectionTitle,
    FaciesProbabilityCube,
    GaussianRandomFields,
    TruncationRule,
  },
})
export default class ElementSettings extends Vue {
  get options () {
    return {
      zone: this.$store.state.options.showNameOrNumber.zone.value,
      region: this.$store.state.options.showNameOrNumber.region.value,
    }
  }

  get title () { return `Settings for ${this.zoneName}`.concat(this.useRegions ? ` / ${this.regionName}` : '') }

  get useRegions () {
    return this.$store.state.regions.use
  }

  // TODO: Combine common logic in zone/regionName
  get zoneName () {
    const current = this.$store.getters.zone
    return isEmpty(current)
      ? ''
      : this.options.zone === 'name'
        ? current.name
        : `Zone ${current.code}`
  }

  get regionName () {
    const current = this.$store.getters.region
    return isEmpty(current)
      ? ''
      : this.options.region === 'name'
        ? current.name
        : `Region ${current.code}`
  }

  get hasFacies () { return Object.keys(this.$store.state.facies.available).length > 0 }

  get expanded () { return this.hasFacies ? [1] : [] }
}
</script>
