<template>
  <selectable-table
    :raw-data="availableZones"
    :on-selection-changed="selectedZones"
    :on-row-clicked="setCurrentZone"
    header-name="Zone"
    @grid-api-ready="setZoneGridApi"
  />
</template>

<script>
import SelectableTable from '@/components/table/SelectableTable'

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
      return this.$store.state.zones.available
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

<style scoped>

</style>
