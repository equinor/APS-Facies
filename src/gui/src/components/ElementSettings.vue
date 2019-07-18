<template>
  <div>
    <h2>{{ title }}</h2>
    <facies-probability-cube
      v-if="hasFacies"
    />
    <truncation-rule />
    <gaussian-random-fields />
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple.vue'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube/index.vue'
import TruncationRule from '@/components/specification/TruncationRule/index.vue'

import { isEmpty } from '@/utils'

@Component({
  components: {
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
}
</script>
