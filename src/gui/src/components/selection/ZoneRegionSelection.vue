<template>
  <v-layout column>
    <zone-selection />
    <choose-region-parameter />
    <region-selection
      v-show="canShowRegions"
    />
  </v-layout>
</template>

<script>
import ChooseRegionParameter from '@/components/selection/dropdown/ChooseRegionParameter'
import RegionSelection from './RegionSelection'
import ZoneSelection from './ZoneSelection'

import { notEmpty } from '@/utils'

export default {
  components: {
    ChooseRegionParameter,
    RegionSelection,
    ZoneSelection,
  },

  computed: {
    canShowRegions () {
      return (
        this.$store.state.regions.use &&
        notEmpty(this.$store.getters.regionParameter)
      )
    },
  },
}
</script>
