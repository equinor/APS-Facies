<template>
  <v-layout
    row
  >
    <v-checkbox
      v-model="useRegions"
      label="Use regions?"
    />
    <choose-parameter
      :disabled="!useRegions"
      regular
      parameter-type="region"
      label="Region parameter"
    />
  </v-layout>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'

import { NoCache } from '@/utils/helpers'

@Component({
  components: {
    ChooseParameter
  },
})
export default class ChooseRegionParameter extends Vue {
  @NoCache
  get useRegions () {
    return this.$store.state.regions.use
  }

  set useRegions (value) {
    this.$store.dispatch('regions/use', { use: value })
  }
}
</script>
