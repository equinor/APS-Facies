<template>
  <v-row :dense="true" no-gutters>
    <v-col>
      <informational-icon
        v-if="parentSelected && isFaciesFromRms"
        :value="value"
        :active="isObserved"
        :current="current"
        message="Observed in well log"
        inactive-message="Not observed"
        icon="observed"
      />
    </v-col>
    <v-col>
      <informational-icon
        :value="value"
        :active="isFaciesFromRms"
        :current="current"
        icon="fromRoxar"
        message="Fetched from RMS"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import type { ID } from '@/utils/domain/types'
import type { GlobalFacies } from '@/utils/domain'

import InformationalIcon from './InformationalIcon.vue'
import { computed } from 'vue'
import { useRootStore } from '@/stores'
import { useFaciesStore } from '@/stores/facies'
import { useZoneStore } from '@/stores/zones'
import { useRegionStore } from '@/stores/regions'

const props = defineProps<{
  value: GlobalFacies
  current?: ID | null
}>()
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
