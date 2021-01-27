<template>
  <v-row
    no-gutters
  >
    <v-col>
      <zone-selection />
      <choose-region-parameter />
      <region-selection
        v-show="canShowRegions"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ChooseRegionParameter from '@/components/selection/dropdown/ChooseRegionParameter.vue'
import RegionSelection from './RegionSelection.vue'
import ZoneSelection from './ZoneSelection.vue'

import { notEmpty } from '@/utils'

@Component({
  components: {
    ChooseRegionParameter,
    RegionSelection,
    ZoneSelection,
  },
})
export default class ZoneRegion extends Vue {
  get canShowRegions (): boolean {
    return (
      this.$store.state.regions.use
      && notEmpty(this.$store.getters.regionParameter)
    )
  }
}
</script>
