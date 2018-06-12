<template>
  <v-container
    align-start
    justify-start
    fluid
  >
    <GridModel/>
    <div v-if="gridModel">
      <zone-region/>
      <facies-table/>
    </div>
  </v-container>
</template>

<script>
import ZoneRegion from '@/components/selection/ZoneRegionSelection'
import GridModel from '@/components/selection/ChooseGridModel'
import FaciesTable from '@/components/selection/FaciesSelection'

export default {
  components: {
    ZoneRegion,
    GridModel,
    FaciesTable
  },

  data () {
    return {
      toggledZoneRegion: false
    }
  },

  computed: {
    panels () {
      return [
        { panel: ZoneRegion, name: 'Zones' },
        { panel: FaciesTable, name: 'Facies' }
      ]
    },

    gridModel () {
      return this.$store.state.selectedGridModel
    }
  }
}
</script>

<style scoped>

</style>
