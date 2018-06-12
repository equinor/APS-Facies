<template>
  <div>
    <selectable-table
      :raw-data="availableZones"
      :on-selection-changed="selectedZones"
      :on-row-clicked="currentZone"
      header-name="Zone"
    />
    <v-form>
      <v-checkbox
        v-model="useRegions"
        label="Use regions?"
      />
    </v-form>
    <div v-if="useRegions">
      <selectable-table
        :raw-data="availableRegions"
        :on-selection-changed="selectedRegions"
        :on-row-clicked="currentRegion"
        header-name="Region"
      />
    </div>
  </div>
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
    }
  },

  computed: {
    availableRegions () {
      return []
    },
    availableZones () {
      return this.getRawData().map(item => {
        return {id: item.id, name: item.name}
      })
    },
  },

  methods: {
    getRawData () {
      // const zones = this.$store.state.availableZones
      return this.$store.state.availableZones
    },
    _dispatchSelectedRows  (event, action) {
      this.$store.dispatch(action, event.api.getSelectedRows())
    },
    _dispatchCurrentSelected (event, action) {
      this.$store.dispatch(action, event.data)
    },
    selectedZones (event) {
      this._dispatchSelectedRows(event, 'selectZones')
    },
    selectedRegions (event) {
      this._dispatchSelectedRows(event, 'selectRegions')
    },
    currentZone (event) {
      this._dispatchCurrentSelected(event, 'currentZone')
    },
    currentRegion (event) {
      this._dispatchCurrentSelected(event, 'currentRegion')
    },
  }
}
</script>

<style scoped>

</style>
