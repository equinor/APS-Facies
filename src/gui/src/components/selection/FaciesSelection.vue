<template>
  <div>
    <facies-table
      :row-data="availableFacies"
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
import FaciesTable from 'Components/table/FaciesTable'

import { forceRefresh } from 'Utils/grid'

// TODO: Ensure change of color is done as a commit / action
// Look for onRow/Data/CellChanged

export default {
  components: {
    FaciesTable,
  },

  data () {
    return {
      faciesTable: [],
      gridApi: null,
    }
  },

  computed: {
    availableFacies () {
      return this.$store.state.facies.available
    },
    selectedFacies () {
      return this.$store.state.facies.current
    }
  },

  methods: {
    setGridApi (api) {
      this.gridApi = api
    },
    add () {
      const emptyFacies = this.newFacies()
      this.$store.dispatch('facies/changed', emptyFacies)
        .then(index => {
          this.forceUpdateGrid()
          this.gridApi.startEditingCell({
            rowIndex: index,
            colKey: 'name'
          })
        })
    },
    remove () {
      this.$store.dispatch('facies/removeSelectedFacies')
        .then(() => {
          this.forceUpdateGrid()
          this.$store.dispatch('facies/current', null)
        })
    },
    newFacies (code = -1, name = null, color = null) {
      if (code < 0) {
        code = 1 + this.$store.state.facies.available
          .map(facies => facies.code)
          .reduce((a, b) => Math.max(a, b), 0)
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
