<template>
  <grid-table
    :row-data="rowData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="gridOptions"
    @grid-api-ready="passGridApiAlong"
  />
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import GridTable from 'Components/table/BaseTable'

export default Vue.extend({
  components: {
    GridTable
  },

  props: {
    rowData: VueTypes.arrayOf(VueTypes.object).isRequired,
    columnDefinitions: VueTypes.arrayOf(VueTypes.object).isRequired,
    additionalGridOptions: VueTypes.object.def({}),
    onRowClicked: VueTypes.func.def(event => {}),
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
  },

  methods: {
    passGridApiAlong (api) {
      this.$emit('grid-api-ready', api)
    }
  },
})
</script>
