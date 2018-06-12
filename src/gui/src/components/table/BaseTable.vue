<template>
  <!-- eslint-disable vue/attribute-hyphenation -->
  <ag-grid-vue
    :gridOptions="gridOptions"
    :style="tableStyle"
    :class="agTheme"
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
      gridOptions: {}
    }
  },

  beforeMount () {
    this.gridOptions = {
      ...this.additionalGridOptions,
      defaultColDef: {
        width: this.defaultColumnWidth
      },
      context: {
        componentParent: this
      },
      onGridReady: function (params) {
        params.api.sizeColumnsToFit()

        window.addEventListener('resize', function () {
          setTimeout(function () {
            params.api.sizeColumnsToFit()
          })
        })
      },
      // Various flags
      enableColResize: true,
    }

    this.gridOptions.columnDefs = this.columnDefinitions
    this.gridOptions.rowData = this.rawData
  },
})
</script>

<style scoped>

</style>
