<template>
  <grid-table
    :raw-data="rawData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="gridOptions"
    @grid-api-ready="passGridApiAlong"
  />
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import GridTable from '@/components/table/BaseTable'
// import {rawDataType} from 'Utils/typing'

export default Vue.extend({
  components: {
    GridTable
  },

  props: {
    rawData: VueTypes.arrayOf(VueTypes.object).isRequired,
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

<style scoped>

</style>
