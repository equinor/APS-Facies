<template>
  <v-container
    align-start
    justify-start
  >
    <grid-model
      @changed="onGridModelSelected"
    />

    <v-expansion-panel
      v-if="currentGridModel"
      v-model="panel"
      expand
    >
      <v-expansion-panel-content>
        <template slot="header">Zones and regions</template>
        <v-card>
          <div v-if="currentGridModel">
            <zone-parameter/>
            <div v-if="zoneParameter">
              <zone-region/>
            </div>
          </div>
          <div v-else>Selection of zones and regions is not available until Grid Model is selected</div>
        </v-card>
      </v-expansion-panel-content>

      <v-expansion-panel-content>
        <template slot="header">Facies</template>
        <v-card>
          <div v-if="currentGridModel">
            <div
              v-if="hasWellParameters"
            >
              <choose-blocked-well-parameter/>
              <choose-blocked-well-log-parameter
                v-if="hasBlockedWellParameter"
              />
              <div
                v-if="hasBlockedWellLogParameter"
              >
                <facies-selection/>
              </div>
            </div>
            <div
              v-else
            >
              <facies-selection/>
            </div>
          </div>
          <div v-else>Selection of facies is not available until Grid Model is selected</div>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-container>
</template>

<script>
import ZoneRegion from '@/components/selection/ZoneRegionSelection'
import GridModel from '@/components/selection/dropdown/ChooseGridModel'
import ZoneParameter from '@/components/selection/dropdown/ChooseZoneParameter'
import FaciesSelection from '@/components/selection/FaciesSelection'
import ChooseBlockedWellParameter from '@/components/selection/dropdown/ChooseBlockedWellParameter'
import ChooseBlockedWellLogParameter from '@/components/selection/dropdown/ChooseBlockedWellLogParameter'

export default {
  components: {
    ZoneRegion,
    GridModel,
    ZoneParameter,
    ChooseBlockedWellParameter,
    ChooseBlockedWellLogParameter,
    FaciesSelection
  },

  data () {
    return {
      toggledZoneRegion: false,
      panel: [false, false],
      disabled: false,
      readonly: false
    }
  },

  computed: {
    hasWellParameters () {
      return this.$store.state.parameters.blockedWell.available.length > 0
    },
    hasBlockedWellLogParameter () {
      return !!this.$store.getters.blockedWellLogParameter
    },
    hasBlockedWellParameter () {
      return !!this.$store.getters.blockedWellParameter
    },

    zoneParameter () {
      return this.$store.state.parameters.zone.selected
    },

    currentGridModel () {
      return this.$store.state.gridModels.current
    }
  },

  methods: {
    onGridModelSelected: function (gridModel) {
      this.panel = [true, true]
    }

  },
}
</script>
