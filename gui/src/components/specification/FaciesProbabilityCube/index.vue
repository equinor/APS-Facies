<template>
  <v-row class="fill-height" align="center" justify="center">
    <v-col>
      <probability-cube-header />
    </v-col>
    <v-col cols="12">
      <facies-probability-cube-table />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import ProbabilityCubeHeader from './header.vue'
import FaciesProbabilityCubeTable from './table.vue'
</script>
