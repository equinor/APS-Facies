<template>
  <div>
    <zone-selection/>
    <v-layout
      v-if="canShowRegions"
      row
    >
      <v-form>
        <v-checkbox
          v-model="useRegions"
          label="Use regions?"
        />
        <!--TODO: Add selection of region parameter-->
      </v-form>
      <choose-region-parameter
        :disabled="!useRegions"
      />
    </v-layout>
    <div v-if="useRegions">
      <selectable-table
        :raw-data="availableRegions"
        :on-selection-changed="selectedRegions"
        :on-row-clicked="setCurrentRegion"
        header-name="Region"
        @grid-api-ready="setRegionGridApi"
      />
    </div>
  </div>
</template>

<script>
import SelectableTable from '@/components/table/SelectableTable'
import ZoneSelection from '@/components/selection/ZoneSelection'
import ChooseRegionParameter from '@/components/selection/dropdown/ChooseRegionParameter'
import { forceRefresh } from '@/utils/grid'

export default {
  components: {
    SelectableTable,
    ChooseRegionParameter,
    ZoneSelection
  },

  data () {
    return {
      useRegions: false,
      gridApis: {},
    }
  },

  computed: {
    availableRegions () {
      return this.$store.state.regions.available
    },
    availableZones () {
      return this.$store.state.zones.available
    },
    canShowRegions () {
      return !!this.$store.state.zones.current
    },
  },

  methods: {
    _dispatchSelectedRows  (event, type) {
      return this.$store.dispatch(type + '/select', event.api.getSelectedRows())
    },
    _dispatchCurrentSelected (event, action) {
      return this.$store.dispatch(action, event.data)
    },
    selectedZones (event) {
      this._dispatchSelectedRows(event, 'zones')
    },
    selectedRegions (event) {
      this._dispatchSelectedRows(event, 'regions')
    },
    setCurrentZone (event) {
      this._dispatchCurrentSelected(event, 'zones/current').then(() => {
        if (this.useRegions) {
          forceRefresh(this.gridApis.region, this.availableRegions)
        }
      })
    },
    setCurrentRegion (event) {
      this._dispatchCurrentSelected(event, 'regions/current')
    },
    setRegionGridApi (api) {
      this.gridApis.region = api
    },
    setZoneGridApi (api) {
      this.gridApis.zone = api
    },
  }
}
</script>

<style scoped>

</style>
