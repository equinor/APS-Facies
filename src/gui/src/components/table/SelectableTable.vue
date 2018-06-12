<template>
  <clickable-row-table
    :raw-data="rawData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="additionalGridOptions"
    :on-row-clicked="onRowClicked"
  />
</template>

<script>
import Vue from 'vue'
import ClickableRowTable from '@/components/table/ClickableRowTable'

export default Vue.extend({
  components: {
    ClickableRowTable
  },

  props: {
    rawData: {
      type: Array,
      required: true
    },
    headerName: {
      type: String,
      required: true
    },
    onSelectionChanged: {
      type: Function,
      required: false,
      default: (event) => {}
    },
    onRowClicked: {
      type: Function,
      required: false,
      default: (event) => {}
    }
  },

  data () {
    return {
      columnDefinitions: [
        {
          headerName: 'Use',
          field: 'id',
          width: 30,
          headerCheckboxSelection: true,
          headerCheckboxSelectionFilteredOnly: true,
          checkboxSelection: true
        },
        {headerName: this.headerName, field: 'name'},
      ],
      additionalGridOptions: {
        suppressRowClickSelection: true,
        rowSelection: 'multiple',
        onSelectionChanged: (event) => { this.onSelectionChanged(event) },
      }
    }
  },

  methods: {
    getSelectedRows () {
      return this.$children[0].$data.gridOptions.api.getSelectedRows()
    }
  },
})
</script>

<style scoped>

</style>
