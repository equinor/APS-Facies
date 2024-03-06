<template>
  <selection-table
    header-name="Region"
    item-type="region"
    no-data-text="A Zone must be selected, before its regions may be shown"
    show-code
    :show-name="showName"
    loading-text="Loading Regions"
  />
</template>

<script setup lang="ts">
import SelectionTable from '@/components/table/SelectionTable.vue'

import { computed } from 'vue'
import { useZoneStore } from '@/stores/zones'

const zoneStore = useZoneStore()

const regions = computed(() => zoneStore.current?.regions ?? [])
const showName = computed(() => regions.value.some((region) => !!region.name))
</script>
