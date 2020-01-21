<template>
  <v-row
    justify="space-between"
    no-gutters
  >
    <v-col cols="3">
      <v-checkbox
        v-model="useRegions"
        label="Use regions?"
      />
    </v-col>
    <v-col cols="9">
      <choose-parameter
        :disabled="!useRegions"
        regular
        parameter-type="region"
        label="Region parameter"
      />
    </v-col>
  </v-row>
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
  get useRegions (): boolean {
    return this.$store.state.regions.use
  }

  set useRegions (value: boolean) {
    this.$store.dispatch('regions/use', { use: value })
  }
}
</script>
