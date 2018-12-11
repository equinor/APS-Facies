<template>
  <v-container
    align-start
    justify-start
  >
    <grid-model />
    <choose-facies-realization-parameter
      v-if="currentGridModel"
    />

    <v-expansion-panel
      v-if="currentGridModel"
      v-model="panel"
      expand
    >
      <v-expansion-panel-content>
        <div slot="header">
          Zones and regions
        </div>
        <v-card>
          <div v-if="currentGridModel">
            <zone-region />
          </div>
          <div v-else>
            Selection of zones and regions is not available until Grid Model is selected
          </div>
        </v-card>
      </v-expansion-panel-content>

      <v-expansion-panel-content>
        <div slot="header">
          Facies
        </div>
        <v-card>
          <div v-if="currentGridModel">
            <div
              v-if="hasWellParameters"
            >
              <choose-blocked-well-parameter />
              <choose-blocked-well-log-parameter
                v-if="hasBlockedWellParameter"
              />
              <div
                v-if="hasBlockedWellLogParameter"
              >
                <facies-selection />
              </div>
            </div>
            <div
              v-else
            >
              <facies-selection />
            </div>
          </div>
          <div v-else>
            Selection of facies is not available until Grid Model is selected
          </div>
        </v-card>
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-container>
</template>

<script>
import ZoneRegion from '@/components/selection/ZoneRegionSelection'
import GridModel from '@/components/selection/dropdown/ChooseGridModel'
import FaciesSelection from '@/components/selection/FaciesSelection'
import ChooseBlockedWellParameter from '@/components/selection/dropdown/ChooseBlockedWellParameter'
import ChooseBlockedWellLogParameter from '@/components/selection/dropdown/ChooseBlockedWellLogParameter'
import ChooseFaciesRealizationParameter from '@/components/selection/dropdown/ChooseFaciesRealizationParameter'

export default {
  components: {
    ChooseFaciesRealizationParameter,
    ZoneRegion,
    GridModel,
    ChooseBlockedWellParameter,
    ChooseBlockedWellLogParameter,
    FaciesSelection
  },

  data () {
    return {
      toggledZoneRegion: false,
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

    currentGridModel () {
      return this.$store.state.gridModels.current
    },
    panel () {
      return this.currentGridModel
        ? [true, true]
        : [false, false]
    }
  }

}
</script>
