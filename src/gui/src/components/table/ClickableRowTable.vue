<template>
  <grid-table
    :raw-data="rawData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="gridOptions"
  />
</template>

<script>
import Vue from 'vue'
import GridTable from '@/components/table/BaseTable'

export default Vue.extend({
  components: {
    GridTable
  },
  props: {
    rawData: {
      type: Array,
      required: true
    },
    columnDefinitions: {
      type: Array,
      required: true
    },
    additionalGridOptions: {
      type: Object,
      required: false,
      default: () => {}
    },
    onRowClicked: {
      type: Function,
      required: false,
      default: (event) => {}
    }
  },

  data () {
    return {
      gridOptions: {}
    }
  },
  beforeMount () {
    this.gridOptions = {
      ...this.additionalGridOptions,
      onRowClicked: (event) => { this.onRowClicked(event) },
    }
  }
})
</script>

<style scoped>

</style>
