<template>
  <selection-table
    header-name="Zone"
    item-type="zone"
    show-name
    show-code
    loading-text="Loading Zones"
  />
</template>

<script setup lang="ts">
import SelectionTable from '@/components/table/SelectionTable.vue'
</script>
