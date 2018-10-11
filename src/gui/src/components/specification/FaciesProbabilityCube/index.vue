<template>
  <v-expansion-panel>
    <v-expansion-panel-content>
      <div slot="header">
        <h2>Probabilities for Facies</h2>
      </div>
      <v-card>
        <v-container>
          <v-layout
            child-flex
            align-center
            justify-start
            row
            fill-height
            wrap
          >
            <probability-cube-header/>
            <facies-probability-cube-table/>
          </v-layout>
        </v-container>
      </v-card>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import ProbabilityCubeHeader from './header'
import FaciesProbabilityCubeTable from './table'

export default {
  components: {
    ProbabilityCubeHeader,
    FaciesProbabilityCubeTable,
  },
}
</script>
