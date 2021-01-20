<template>
  <v-row
    class="fill-height"
    align="center"
    justify="center"
  >
    <v-col>
      <probability-cube-header />
    </v-col>
    <v-col cols="12">
      <facies-probability-cube-table />
    </v-col>
  </v-row>
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
