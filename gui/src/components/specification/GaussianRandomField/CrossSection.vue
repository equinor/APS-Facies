<template>
  <v-row class="ma-2">
    <!--Cross section-->
    <v-col>
      <v-select
        v-model="type"
        :items="['IJ', 'IK', 'JK']"
        label="Cross section type"
        required
        variant="underlined"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import type {
  CrossSectionType,
} from '@/utils/domain/gaussianRandomField/crossSection'

import { computed } from 'vue'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'

const crossSectionStore = useGaussianRandomFieldCrossSectionStore()

const type = computed({
  get: () => crossSectionStore.current.type,
  set: (value: CrossSectionType) => {
    crossSectionStore.changeType(value)
  },
})
</script>
