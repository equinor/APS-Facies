<template>
  <selectable-item-list
    item-type="region"
    :show-name="showName"
    no-data-text="A Zone must be selected, before its regions may be shown"
  />
</template>

<script setup lang="ts">
import SelectableItemList from '@/components/selection/SelectableItemList.vue'

import { computed } from 'vue'
import { useZoneStore } from '@/stores/zones'

const zoneStore = useZoneStore()

const regions = computed(() => zoneStore.current?.regions ?? [])
const showName = computed(() => regions.value.some((region) => !!region.name))
</script>
