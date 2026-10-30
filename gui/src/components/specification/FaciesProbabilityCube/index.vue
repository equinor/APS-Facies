<template>
  <div class="d-flex flex-column ga-2 px-2 pb-2">
    <probability-cube-header />
    <facies-probability-cube-table />
  </div>
</template>

<script setup lang="ts">
import ProbabilityCubeHeader from './header.vue'
import FaciesProbabilityCubeTable from './table.vue'
</script>
