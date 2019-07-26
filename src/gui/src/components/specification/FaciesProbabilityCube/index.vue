<template>
  <v-layout
    align-center
    justify-center
    fill-height
    wrap
  >
    <v-flex>
      <probability-cube-header />
    </v-flex>
    <v-flex xs12>
      <facies-probability-cube-table />
    </v-flex>
  </v-layout>
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
