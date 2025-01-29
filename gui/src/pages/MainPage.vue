<template>
  <v-container fluid>
    <v-row
      v-if="loading"
      class="d-flex align-content-center flex-column align-center"
    >
      <v-progress-circular :size="70" indeterminate />
      <span>{{ loadingMessage }}</span>
    </v-row>
    <v-row v-else>
      <v-col cols="4" class="pa-0">
        <scrollable-area>
          <selection />
        </scrollable-area>
      </v-col>
      <v-col cols="4">
        <scrollable-area>
          <preview v-if="hasSimulations" />
        </scrollable-area>
      </v-col>
      <v-col cols="4">
        <scrollable-area>
          <settings v-if="canSpecifyModelSettings" />
        </scrollable-area>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import Selection from '@/components/ElementSelection.vue'
import Settings from '@/components/ElementSettings.vue'
import Preview from '@/components/ElementPreview.vue'
import ScrollableArea from '@/components/baseComponents/ScrollableArea.vue'

import type { GaussianRandomField } from '@/utils/domain'
import { computed } from 'vue'
import { useRootStore } from '@/stores'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'

const rootStore = useRootStore()
const fieldStore = useGaussianRandomFieldStore()

const canSpecifyModelSettings = computed<boolean>(
  () => rootStore.canSpecifyModelSettings,
)
const loading = computed<boolean>(() => rootStore.loading)
const loadingMessage = computed<string>(() => rootStore.loadingMessage)
const fields = computed<GaussianRandomField[]>(() => fieldStore.selected)
const hasSimulations = computed<boolean>(() => fields.value.length > 0)
</script>
