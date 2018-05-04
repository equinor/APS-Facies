<template>
  <v-container
    align-start
    justify-start
    fluid
  >
    <GridModel/>
    <div v-if="gridModel">
      <v-expansion-panel expand>
        <v-expansion-panel-content
          v-for="{panel, name} in panels"
          :key="name"
        >
          <div slot="header">{{ name }}</div>
          <v-card>
            <v-container :is="panel"/>
          </v-card>
        </v-expansion-panel-content>
      </v-expansion-panel>
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
