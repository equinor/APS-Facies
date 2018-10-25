<template>
  <div>
    <h2>{{ title }}</h2>
    <facies-probability-cube
      v-if="hasFacies"
    />
    <truncation-rule/>
    <gaussian-random-fields/>
  </div>
</template>

<script>
import { mapState } from 'vuex'

import GaussianRandomFields from '@/components/specification/GaussianRandomField/multiple'
import FaciesProbabilityCube from '@/components/specification/FaciesProbabilityCube'
import TruncationRule from '@/components/specification/TruncationRule'

import { isEmpty } from '@/utils'

export default {
  components: {
    FaciesProbabilityCube,
    GaussianRandomFields,
    TruncationRule,
  },

  computed: {
    ...mapState({
      options: state => {
        return {
          zone: state.options.showNameOrNumber.zone.show,
          region: state.options.showNameOrNumber.region.show,
        }
      }
    }),
    title () { return `Settings for ${this.zoneName}`.concat(this.useRegions ? ` / ${this.regionName}` : '') },
    useRegions () {
      return this.$store.state.regions.use
    },
    // TODO: Combine common logic in zone/regionName
    zoneName () {
      const current = this.$store.getters.zone
      return isEmpty(current)
        ? ''
        : this.options.zone === 'name'
          ? current.name
          : `Zone ${current.code}`
    },
    regionName () {
      const current = this.$store.getters.region
      return isEmpty(current)
        ? ''
        : this.options.region === 'name'
          ? current.name
          : `Region ${current.code}`
    },
    zoneModels () {
      const selectedZones = this.$store.getters['zones/selected']
      // const currentZone = this.$store.state.zones.current

      if (selectedZones == null) {
        return []
      } else {
        const models = []
        const zones = this.$store.state.zones.available
        selectedZones.forEach(function (zoneId) {
          const zone = zones[`${zoneId}`]
          models.push({ zoneNumber: zone.code, regionNumber: 0 })
        })
        return models
      }
    },
    hasFacies () { return Object.keys(this.$store.state.facies.available).length > 0 },
  },
}
</script>
