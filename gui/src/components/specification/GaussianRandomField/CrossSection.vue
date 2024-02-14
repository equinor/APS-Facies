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

import { useStore } from '../../../store'
import { computed } from 'vue'

const store = useStore()

const crossSection = computed<Optional<CrossSection>>(
  () => store.getters['gaussianRandomFields/crossSections/current'],
)

const type = computed({
  get: () => crossSection.value?.type ?? 'IJ',
  set: (value: CrossSectionType) =>
    store.dispatch('gaussianRandomFields/crossSections/changeType', {
      id: crossSection.value?.id,
      type: value,
    }),
})
</script>
