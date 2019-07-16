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
            column
            fill-height
            wrap
          >
            <probability-cube-header />
            <facies-probability-cube-table />
          </v-layout>
        </v-container>
      </v-card>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ProbabilityCubeHeader from './header.vue'
import FaciesProbabilityCubeTable from './table.vue'

@Component({
  components: {
    ProbabilityCubeHeader,
    FaciesProbabilityCubeTable,
  },
})
export default class FaciesProbabilityCube extends Vue {
}
</script>
