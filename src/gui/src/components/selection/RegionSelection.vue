<template>
  <selection-table
    header-name="Regions"
    item-type="region"
    no-data-text="A Zone must be selected, before its regions may be shown"
    show-name
    show-code
  />
</template>

<script>
import SelectionTable from '@/components/table/SelectionTable'

export default {
  components: {
    SelectionTable
  },
}
</script>
