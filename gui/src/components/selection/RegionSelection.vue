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

import { Region } from '@/utils/domain'
import { useStore } from '../../store'
import { computed } from 'vue'

const store = useStore()

const regions = computed<Region[]>(() => store.getters.regions)
const showName = computed(() => regions.value.some((region) => !!region.name))
</script>
