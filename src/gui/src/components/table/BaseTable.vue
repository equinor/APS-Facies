<template>
  <!-- eslint-disable vue/attribute-hyphenation -->
  <ag-grid-vue
    :gridOptions="gridOptions"
    :rowData="rawData"
    :style="tableStyle"
    :class="agTheme"
    :on-grid-ready="onGridReady"
    ag-row-hover
  />
</template>

<script>
import Vue from 'vue'
import { AgGridVue } from 'ag-grid-vue'

export default Vue.extend({
  components: {
    AgGridVue,
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
    tableStyle: {
      type: String,
      default: 'width: 30rem; height: 10rem;'
    },
    agTheme: {
      type: String,
      default: 'ag-theme-balham'
    },
    defaultColumnWidth: {
      type: Number,
      required: false,
      default: 100
    },
    additionalGridOptions: {
      type: Object,
      required: false,
      default: () => {}
    }
  },

  data () {
    return {
      gridOptions: {},
      gridApi: null,
    }
  },

  beforeMount () {
    this.gridOptions = {
      defaultColDef: {
        width: this.defaultColumnWidth
      },
      context: {
        componentParent: this
      },
      // Various flags
      enableColResize: true,
      ...this.additionalGridOptions,
    }

    this.gridOptions.columnDefs = this.columnDefinitions
    // this.gridOptions.rowData = this.rawData
  },

  methods: {
    onGridReady: function (params) {
      const gridApi = params.api
      gridApi.sizeColumnsToFit()

      window.addEventListener('resize', function () {
        setTimeout(function () {
          gridApi.sizeColumnsToFit()
        })
      })
      this.gridApiReady(gridApi)
    },

    gridApiReady (api) {
      this.gridApi = api
      this.$emit('grid-api-ready', api)
    },
  },
})
</script>

<style scoped>

</style>
