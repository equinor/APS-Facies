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
import { Optional } from '@/utils/typing'
import CrossSection, {
  CrossSectionType,
} from '@/utils/domain/gaussianRandomField/crossSection'

import { computed } from 'vue'
import { useGaussianRandomFieldCrossSectionStore } from '@/stores/gaussian-random-fields/cross-sections'

const crossSectionStore = useGaussianRandomFieldCrossSectionStore()

const crossSection = computed<Optional<CrossSection>>(
  () => crossSectionStore.current,
)

const type = computed({
  get: () => crossSection.value?.type ?? 'IJ',
  set: (value: CrossSectionType) => {
    if (!crossSection.value) return
    crossSectionStore.changeType(crossSection.value.id, value)
  },
})
</script>
