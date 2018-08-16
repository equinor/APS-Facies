<template>
  <clickable-table
    :row-data="rowData"
    :column-definitions="columnDefinitions"
    :additional-grid-options="additionalGridOptions"
    @grid-api-ready="setGridApi"
  />
</template>

<script>
import VueTypes from 'vue-types'
import ClickableTable from 'Components/table/ClickableRowTable'
import ColorPicker from 'Components/table/cell-renderer/ColorPicker'
import ColorRenderer from 'Components/table/cell-renderer/ColorRenderer'

// TODO: Ensure change of color is done as a commit / action
// Look for onRow/Data/CellChanged

const maximumColumnWidth = 75

export default {
  components: {
    ClickableTable,
  },

  props: {
    rowData: VueTypes.arrayOf(VueTypes.object).isRequired
  },

  data () {
    return {
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
        {headerName: 'Facies', field: 'name', type: 'editable'},
        {headerName: 'Code', field: 'code', type: ['editable', 'narrow']},
        {headerName: 'Color', field: 'color', type: ['editable', 'narrow', 'colorCell', 'onceClickable']}
      ]
    }
  },

  methods: {
    setGridApi (api) {
      this.$emit('grid-api-ready', api)
    },
    faciesChanged (event) {
      this.$store.dispatch('facies/changed', event.data)
    },
    selectedFaciesRow (event) {
      const selectedRows = event.api.getSelectedRows()
      if (selectedRows.length > 0) {
        const clickedCell = event.api.getFocusedCell()
        if (clickedCell.column.getColId() === 'color') {
          // TODO: Abort selection animation
          // event.api.deselectAll()
        } else {
          this.$store.dispatch('facies/current', selectedRows[0])
        }
      } else {
        //
      }
    },
  }
}
</script>
