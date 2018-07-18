<template>
  <v-layout column>
    <v-flex xs12>
      <zone-selection/>
    </v-flex>
    <v-layout
      v-if="canShowRegions"
      row
    >
      <v-checkbox
        v-model="useRegions"
        label="Use regions?"
      />
      <!--TODO: Add selection of region parameter-->
      <choose-region-parameter
        :disabled="!useRegions"
      />
    </v-layout>
    <div v-if="!!$store.state.parameters.region.selected">
      <selectable-table
        :row-data="availableRegions"
        :on-selection-changed="selectedRegions"
        :on-row-clicked="setCurrentRegion"
        header-name="Region"
        @grid-api-ready="setRegionGridApi"
      />
    </div>
  </v-layout>
</template>

<script>
import SelectableTable from 'Components/table/SelectableTable'
import ZoneSelection from 'Components/selection/ZoneSelection'
import ChooseRegionParameter from 'Components/selection/dropdown/ChooseRegionParameter'

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
      return this.$store.getters.zone.regions.available
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
    selectedRegions (event) {
      return this.$store.dispatch('zones/regions/select', {zone: this.$store.state.zones.current, regions: event.api.getSelectedRows()})
    },
    // setCurrentZone (event) {
    //   this._dispatchCurrentSelected(event, 'zones/current').then(() => {
    //     if (this.useRegions) {
    //       forceRefresh(this.gridApis.region, this.availableRegions)
    //     }
    //   })
    // },
    setCurrentRegion (event) {
      this._dispatchCurrentSelected(event, 'zones/regions/current')
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
