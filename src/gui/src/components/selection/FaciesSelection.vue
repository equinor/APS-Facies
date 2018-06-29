<template>
  <div>
    <facies-table
      :raw-data="faciesTable"
      :column-definitions="columnDefinitions"
      :additional-grid-options="additionalGridOptions"
      @grid-api-ready="setGridApi"
    />
    <div>
      <v-btn
        color="info"
        @click="add"
      >Add Facies</v-btn>
      <v-btn
        :disabled="!selectedFacies"
        color="warning"
        @click="remove"
      >Remove Facies</v-btn>
    </div>
  </div>
</template>

<script>
import GridTable from 'Components/table/ClickableRowTable'
import ColorPicker from 'Components/table/cell-renderer/ColorPicker'
import ColorRenderer from 'Components/table/cell-renderer/ColorRenderer'

import { forceRefresh } from '@/utils/grid'

// TODO: Ensure change of color is done as a commit / action
// Look for onRow/Data/CellChanged

const maximumColumnWidth = 75

export default {
  components: {
    FaciesTable: GridTable,
  },

  data () {
    return {
      faciesTable: [],
      gridApi: null,
      additionalGridOptions: {
        deltaRowDataMode: true,
        rowSelection: 'single',
        getRowNodeId: data => { return data.code },
        onSelectionChanged: event => { this.selectedFaciesRow(event) },
        columnTypes: {
          'editable': {editable: true, onCellValueChanged: (event) => { this.faciesChanged(event) }}, // FIXME: Ensure the grid itself do not update values
          'narrow': {maxWidth: maximumColumnWidth},
          'colorCell': {cellRendererFramework: ColorRenderer, cellEditorFramework: ColorPicker, cellStyle: (params) => { return {backgroundColor: params.value} }},
          'onceClickable': {singleClickEdit: true}, // FIXME: Ensure works
        }
      },
      columnDefinitions: [
        {headerName: 'Name', field: 'name', type: 'editable'},
        {headerName: 'Code', field: 'code', type: ['editable', 'narrow']},
        {headerName: 'Color', field: 'color', type: ['editable', 'narrow', 'colorCell', 'onceClickable']}
      ]
    }
  },

  computed: {
    availableFacies () {
      return this.$store.state.availableFacies
    },
    selectedFacies () {
      return this.$store.state.currentFacies
    }
  },

  created () {
    this.faciesTable = this.availableFacies
  },

  methods: {
    setGridApi (api) {
      this.gridApi = api
    },
    add () {
      const emptyFacies = this.newFacies()
      this.$store.dispatch('faciesChanged', emptyFacies)
        .then(index => {
          this.forceUpdateGrid()
          this.gridApi.startEditingCell({
            rowIndex: index,
            colKey: 'name'
          })
        })
    },
    remove () {
      this.$store.dispatch('removeSelectedFacies')
        .then(() => {
          this.forceUpdateGrid()
          this.$store.dispatch('currentFacies', null)
        })
    },
    faciesChanged (event) {
      this.$store.dispatch('faciesChanged', event.data)
    },
    selectedFaciesRow (event) {
      const selectedRows = event.api.getSelectedRows()
      if (selectedRows.length > 0) {
        const clickedCell = event.api.getFocusedCell()
        if (clickedCell.column.getColId() === 'color') {
          // TODO: Abort selection animation
          // event.api.deselectAll()
        } else {
          this.$store.dispatch('currentFacies', selectedRows[0])
        }
      } else {
        //
      }
    },
    newFacies (code = -1, name = null, color = null) {
      if (code < 0) {
        code = 1 + this.$store.state.availableFacies
          .map(facies => facies.code)
          .reduce((a, b) => Math.max(a, b))
      }
      if (name === null) {
        name = `F${code}`
      }
      if (color === null) {
        // TODO: Select a color from pallet
        color = '#030303'
      }
      return {code, name, color}
    },
    forceUpdateGrid () {
      forceRefresh(this.gridApi, this.availableFacies)
    }
  }
}
</script>

<style scoped>

</style>
