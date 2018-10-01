<template>
  <selection-table
    header-name="Zone"
    item-type="zone"
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
