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
import { computed } from 'vue'
import { useRegionStore } from '@/stores/regions'
import { useParameterRegionStore } from '@/stores/parameters/region'

const regionStore = useRegionStore()
const regionParameterStore = useParameterRegionStore()
const canShowRegions = computed(
  () => regionStore.use && notEmpty(regionParameterStore.selected),
)
</script>
