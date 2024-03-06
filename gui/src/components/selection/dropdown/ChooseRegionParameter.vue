<template>
  <v-row justify="space-between" align="center" no-gutters>
    <v-col cols="0">
      <warning-dialog ref="warning" html />
    </v-col>
    <v-col cols="4">
      <v-checkbox v-model="useRegions" label="Use regions" />
    </v-col>
    <v-col cols="8">
      <choose-parameter
        :disabled="!useRegions"
        regular
        parameter-type="region"
        label="Region parameter"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'
import WarningDialog from '@/components/dialogs/JobSettings/WarningDialog.vue'

import { computed } from 'vue'
import { useRegionStore } from '@/stores/regions'

const regionStore = useRegionStore()

const useRegions = computed({
  get: () => regionStore.use,
  set: (value: boolean) => regionStore.setUse(value),
})
</script>
