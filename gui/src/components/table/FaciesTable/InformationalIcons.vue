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
import { ID } from '@/utils/domain/types'
import { GlobalFacies } from '@/utils/domain'

import InformationalIcon from './InformationalIcon.vue'
import { useStore } from '../../../store'
import { computed } from 'vue'

type Props = {
  value: GlobalFacies
  current?: ID
}
const props = defineProps<Props>()
const store = useStore()

const isObserved = computed(() =>
  props.value.isObserved({
    zone: store.getters.zone,
    region: store.getters.region,
  }),
)

const isFaciesFromRms = computed(() =>
  store.getters['facies/isFromRMS'](props.value),
)

const parentSelected = computed(() => {
  const zoneSelected = !!store.getters.zone
  if (store.getters.useRegions) {
    const regionSelected = !!store.getters.region
    return zoneSelected && regionSelected
  }
  return zoneSelected
})
</script>
