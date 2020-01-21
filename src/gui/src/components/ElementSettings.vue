<template>
  <v-container
    class="align justify center"
    fluid
  >
    <v-expansion-panels
      v-model="expanded"
      accordion
      multiple
    >
      <section-title>{{ title }}</section-title>
      <v-expansion-panel
        v-tooltip.bottom-start="!hasFacies && 'No Facies has been selected'"
        :disabled="!hasFacies"
      >
        <v-expansion-panel-header>
          <section-title>Probabilities for Facies</section-title>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <facies-probability-cube />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel
        v-tooltip.bottom="!hasEnoughFacies && 'Too few Facies has been selected'"
        :disabled="!hasEnoughFacies"
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
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator'

import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple.vue'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube/index.vue'
import TruncationRule from '@/components/specification/TruncationRule/index.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { isEmpty } from '@/utils'

import { Facies } from '@/utils/domain'

type Option = 'number' | 'name'

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
  get options (): { zone: Option, region: Option } {
    const showNameOrNumber = this.$store.state.options.showNameOrNumber
    return {
      zone: showNameOrNumber.zone.value,
      region: showNameOrNumber.region.value,
    }
  }

  get expanded (): number[] { return this.$store.getters['panels/settings'] }
  set expanded (indices) { this.$store.dispatch('panels/change', { type: 'settings', indices }) }

  get title (): string { return `Settings for ${this.zoneName}`.concat(this.useRegions ? ` / ${this.regionName}` : '') }

  get useRegions (): boolean {
    return this.$store.state.regions.use
  }

  // TODO: Combine common logic in zone/regionName
  get zoneName (): string {
    const current = this.$store.getters.zone
    return isEmpty(current)
      ? ''
      : this.options.zone === 'name'
        ? current.name
        : `Zone ${current.code}`
  }

  get regionName (): string {
    const current = this.$store.getters.region
    return isEmpty(current)
      ? ''
      : this.options.region === 'name'
        ? current.name
        : `Region ${current.code}`
  }

  get _facies (): Facies[] { return this.$store.getters['facies/selected'] }

  get hasFacies (): boolean { return this._facies.length > 0 }

  get hasEnoughFacies (): boolean { return this._facies.length >= 2 /* TODO: Use a constant */ }

  @Watch('_facies', { deep: true })
  async truncationRuleVisibility (): Promise<void> {
    await this.$store.dispatch(`panels/${this.hasEnoughFacies ? 'open' : 'close'}`, { type: 'settings', panel: 'truncationRule' })
    if (!this.hasFacies) {
      await this.$store.dispatch('panels/close', { type: 'settings', panel: ['truncationRule', 'faciesProbability'] })
    }
  }
}
</script>
