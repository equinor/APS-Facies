<template>
  <v-row
    dense
    no-gutters
  >
    <v-col>
      <informational-icon
        v-if="parentSelected && isFaciesFromRms"
        :value="value"
        :active="isObserved"
        :current="current"
        message="Observed in well log"
        inactive-message="Not observed"
        icon="observed"
      />
    </v-col>
    <v-col>
      <informational-icon
        :value="value"
        :active="isFaciesFromRms"
        :current="current"
        icon="fromRoxar"
        message="Fetched from RMS"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { ID } from '@/utils/domain/types'
import { GlobalFacies } from '@/utils/domain'

import InformationalIcon from './InformationalIcon.vue'

@Component({
  components: {
    InformationalIcon,
  },
})
export default class InformationalIcons extends Vue {
  @Prop({ required: true })
  readonly value!: GlobalFacies

  @Prop({ default: undefined })
  readonly current?: ID

  get isObserved (): boolean {
    return this.value.isObserved({
      zone: this.$store.getters.zone,
      region: this.$store.getters.region,
    })
  }

  get isFaciesFromRms (): boolean {
    return this.$store.getters['facies/isFromRMS'](this.value)
  }

  get parentSelected (): boolean {
    const zoneSelected = !!this.$store.getters.zone
    if (this.$store.getters.useRegions) {
      const regionSelected = !!this.$store.getters.region
      return zoneSelected && regionSelected
    }
    return zoneSelected
  }
}
</script>
