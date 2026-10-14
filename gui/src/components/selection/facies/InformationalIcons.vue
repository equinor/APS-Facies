<template>
  <div class="d-flex align-center ga-2">
    <v-icon
      v-if="isFaciesFromRms && parentSelected"
      v-tooltip.bottom="isObserved ? 'Observed in well log' : 'Not observed'"
      :icon="isObserved ? '$observed' : '$observedNegated'"
      size="small"
      class="fa-fw"
    />
    <span class="source-slot d-flex justify-center">
      <v-icon
        v-tooltip.bottom="
          isFaciesFromRms ? 'Fetched from RMS' : 'Added manually'
        "
        :icon="isFaciesFromRms ? '$fromRoxar' : '$createdByUser'"
        size="small"
        class="fa-fw"
      />
    </span>
  </div>
</template>

<script setup lang="ts">
import type { GlobalFacies } from '@/utils/domain'

import { computed } from 'vue'
import { useRootStore } from '@/stores'
import { useFaciesStore } from '@/stores/facies'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'

const props = defineProps<{ value: GlobalFacies }>()
const rootStore = useRootStore()
const zoneStore = useZoneStore()
const regionStore = useRegionStore()
const faciesStore = useFaciesStore()

const isObserved = computed(() => props.value.isObserved(rootStore.parent))

const isFaciesFromRms = computed(() => faciesStore.isFromRMS(props.value))

const parentSelected = computed(() => {
  const zoneSelected = !!zoneStore.current
  if (regionStore.use) {
    const regionSelected = !!regionStore.current
    return zoneSelected && regionSelected
  }
  return zoneSelected
})
</script>

<style lang="scss" scoped>
.source-slot {
  width: 2em;
}
</style>
