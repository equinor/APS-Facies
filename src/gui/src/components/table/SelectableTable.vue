<template>
  <clickable-row-table
    :raw-data="rawData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="additionalGridOptions"
    :on-row-clicked="onRowClicked"
    @grid-api-ready="passGridApiAlong"
  />
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import ClickableRowTable from '@/components/table/ClickableRowTable'

export default Vue.extend({
  components: {
    ClickableRowTable
  },

  props: {
    rawData: VueTypes.arrayOf(VueTypes.object).isRequired,
    headerName: VueTypes.string.isRequired,
    onSelectionChanged: VueTypes.func.def(event => {}),
    onRowClicked: VueTypes.func.def(event => {}),
  },

  data () {
    return {
      gridApi: null,
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
    passGridApiAlong (api) {
      this.gridApi = api
      this.$emit('grid-api-ready', api)
    },
    getSelectedRows () {
      return this.gridApi.getSelectedRows()
    }
  },
})
</script>

<style scoped>

</style>
