<template>
  <v-container
    align-start
    justify-start
  >
    <grid-model/>
    <div v-if="currentGridModel">
      <zone-parameter/>
      <div v-if="zoneParameter">
        <zone-region/>
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
    </div>
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
      toggledZoneRegion: false
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
  }
}
</script>
