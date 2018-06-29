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
        @grid-api-ready="setRegionGridApi"
      />
    </div>
  </div>
</template>

<script>
import SelectableTable from '@/components/table/SelectableTable'
import { forceRefresh } from '@/utils/grid'

export default {
  components: {
    SelectableTable
  },

  data () {
    return {
      useRegions: false,
      gridApis: {},
    }
  },

  computed: {
    availableRegions () {
      const currentZone = this.$store.state.currentZone
      if (currentZone) {
        if (currentZone.regions.length > 0) {
          return currentZone.regions
        } else {
          // The given zone has not regions
          // TODO: Give message saying the zone has no regions
        }
      } else {
        // No zone has been selected
        // TODO: Give message saying you have to select a zone
      }
      return currentZone ? currentZone.regions : []
    },
    availableZones () {
      return this.getRawData()
    },
  },

  methods: {
    getRawData () {
      return this.$store.state.availableZones
    },
    _dispatchSelectedRows  (event, action) {
      return this.$store.dispatch(action, event.api.getSelectedRows())
    },
    _dispatchCurrentSelected (event, action) {
      return this.$store.dispatch(action, event.data)
    },
    selectedZones (event) {
      this._dispatchSelectedRows(event, 'selectZones')
    },
    selectedRegions (event) {
      this._dispatchSelectedRows(event, 'selectRegions')
    },
    currentZone (event) {
      this._dispatchCurrentSelected(event, 'currentZone').then(() => {
        if (this.useRegions) {
          forceRefresh(this.gridApis.region, this.availableRegions)
        }
      })
    },
    currentRegion (event) {
      this._dispatchCurrentSelected(event, 'currentRegion')
    },
    setRegionGridApi (api) {
      this.gridApis.region = api
    },
  }
}
</script>

<style scoped>

</style>
