<template>
  <selectable-table
    :row-data="availableZones"
    :on-selection-changed="selectedZones"
    :on-row-clicked="setCurrentZone"
    header-name="Zone"
    @grid-api-ready="setZoneGridApi"
  />
</template>

<script>
import SelectableTable from 'Components/table/SelectableTable'

export default {
  components: {
    SelectableTable
  },

  data () {
    return {
      useRegions: false,
      gridApi: {},
    }
  },

  computed: {
    availableZones () {
      const zones = this.$store.state.zones.available
      return Object.keys(zones).map(id => { return {id, name: zones[`${id}`].name} })
    }
  },

  methods: {
    selectedZones (event) {
      return this.$store.dispatch('zones/select', event.api.getSelectedRows())
    },
    setCurrentZone (event) {
      return this.$store.dispatch('zones/current', event.data)
    },
    setZoneGridApi (api) {
      this.gridApi = api
    },
  }
}
</script>
