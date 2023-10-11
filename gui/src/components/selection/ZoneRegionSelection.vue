<template>
  <v-row no-gutters>
    <v-col>
      <zone-selection />
      <choose-region-parameter />
      <region-selection v-show="canShowRegions" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import ChooseRegionParameter from '@/components/selection/dropdown/ChooseRegionParameter.vue'
import RegionSelection from './RegionSelection.vue'
import ZoneSelection from './ZoneSelection.vue'

import { notEmpty } from '@/utils'
import { useStore } from '../../store'
import { computed } from 'vue'

const store = useStore()

const canShowRegions = computed(
  () => store.state.regions.use && notEmpty(store.getters.regionParameter),
)
</script>
