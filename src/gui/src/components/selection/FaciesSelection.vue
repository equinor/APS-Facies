<template>
  <div>
    <facies-table
      :raw-data="availableFacies"
      :column-definitions="columnDefinitions"
      :on-row-clicked="selectedFaciesRow"
      :additional-grid-options="additionalGridOptions"
    />
    <div>
      <v-btn color="info">Add Facies</v-btn>
      <v-btn color="warning">Remove Facies</v-btn>
    </div>
  </div>
</template>

<script>
import GridTable from '@/components/table/ClickableRowTable'
import ColorPicker from '@/components/ColorPicker'
import ColorRenderer from '@/components/ColorRenderer'

// TODO: Ensure change of color is done as a commit / action
// Look for onRow/Data/CellChanged

export default {
  components: {
    FaciesTable: GridTable,
  },

  data () {
    return {
      additionalGridOptions: {
        singleClickEdit: true,
      },
      columnDefinitions: [
        {headerName: 'Name', field: 'name'},
        {headerName: 'Code', field: 'code', maxWidth: 75},
        {
          headerName: 'Color',
          field: 'color',
          cellRendererFramework: ColorRenderer,
          cellEditorFramework: ColorPicker,
          cellStyle: (params) => { return {backgroundColor: params.value} },
          editable: true,
          maxWidth: 75
        }
      ]
    }
  },

  computed: {
    availableFacies () {
      return this.$store.state.availableFacies
    }
  },

  methods: {
    selectedFaciesRow (event) {
      const clickedCell = event.api.getFocusedCell()
      if (clickedCell.column.getColId() !== 'color') {
        console.log(event.data)
      }
    }
  }
}
</script>

<style scoped>

</style>
