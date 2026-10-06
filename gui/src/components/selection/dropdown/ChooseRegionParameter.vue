<template>
  <div class="d-flex flex-column ga-2">
    <warning-dialog ref="warning" html />
    <v-checkbox
      v-model="useRegions"
      label="Use regions"
      density="compact"
      hide-details
      class="use-regions"
    />
    <choose-parameter
      :disabled="!useRegions"
      regular
      parameter-type="region"
      label="Region parameter"
    />
  </div>
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

<style lang="scss" scoped>
.use-regions :deep(.v-label) {
  padding-left: 8px;
}
</style>
