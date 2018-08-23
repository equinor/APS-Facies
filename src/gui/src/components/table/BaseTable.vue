<template>
  <!-- eslint-disable vue/attribute-hyphenation -->
  <ag-grid-vue
    :gridOptions="gridOptions"
    :rowData="rowData"
    :style="tableStyle"
    :class="agTheme"
    :on-grid-ready="onGridReady"
    ag-row-hover
  />
</template>

<script>
import Vue from 'vue'
import VueTypes from 'vue-types'
import { AgGridVue } from 'ag-grid-vue'

export default Vue.extend({
  components: {
    AgGridVue,
  },

  props: {
    rowData: VueTypes.array.isRequired,
    columnDefinitions: VueTypes.array.isRequired,
    agTheme: VueTypes.string.def('ag-theme-balham'),
    defaultColumnWidth: VueTypes.integer.def(100),
    additionalGridOptions: VueTypes.object,
  },

  data () {
    return {
      gridOptions: {},
      gridApi: null,
      tableStyle: {
        width: '30rem',
        height: '10rem',
      },
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
  },

  mounted () {
    this.resize()
  },

  methods: {
    onGridReady (params) {
      const gridApi = params.api
      gridApi.sizeColumnsToFit()

      this.gridApiReady(gridApi)
    },

    gridApiReady (api) {
      this.gridApi = api
      this.$emit('grid-api-ready', api)
    },

    resize () {
      this.tableStyle.width = this.$parent.$el.clientWidth
    },
  },
})
</script>
