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

import { ID } from '@/utils/domain/types'

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
      zone: this.$store.state.options.showNameOrNumber.zone.show,
      region: this.$store.state.options.showNameOrNumber.region.show,
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

  get zoneModels () {
    const selectedZones = this.$store.getters['zones/selected']
    // const currentZone = this.$store.state.zones.current

    if (selectedZones == null) {
      return []
    } else {
      const models: { zoneNumber: number, regionNumber: number }[] = []
      const zones = this.$store.state.zones.available
      selectedZones.forEach(function (zoneId: ID) {
        const zone = zones[`${zoneId}`]
        models.push({ zoneNumber: zone.code, regionNumber: 0 })
      })
      return models
    }
  }

  get hasFacies () { return Object.keys(this.$store.state.facies.available).length > 0 }
}
</script>
