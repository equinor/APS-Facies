<template>
  <v-container class="fill-height" fluid>
    <v-row v-if="loading">
      <v-col cols="12" justify="center" align="center">
        <v-progress-circular :size="70" indeterminate />
        <span>{{ loadingMessage }}</span>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="4">
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

import { GaussianRandomField } from '@/utils/domain'
import { useStore } from '../store'
import { computed } from 'vue'

const store = useStore()
// TODO: Typing of getters.canSpecifyModelSettings is wrong
const canSpecifyModelSettings = computed<boolean>(
  () => store.getters.canSpecifyModelSettings,
)
const loading = computed<boolean>(() => store.state._loading.value)
const loadingMessage = computed<string>(() => store.state._loading.message)
const fields = computed<GaussianRandomField[]>(() =>
  Object.values(store.getters.fields),
)
const hasSimulations = computed<boolean>(() => fields.value.length > 0)
</script>
