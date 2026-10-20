<template>
  <div class="d-flex flex-column ga-3">
    <div class="d-flex flex-column ga-2">
      <action-button block @click="add">Add facies</action-button>
      <action-button block disabled>Add filter</action-button>
    </div>
    <facies-list />
  </div>
</template>

<script setup lang="ts">
import ActionButton from '@/components/baseComponents/ActionButton.vue'
import FaciesList from '@/components/selection/facies/FaciesList.vue'

import { useGlobalFaciesStore } from '@/stores/facies/global'

const faciesGlobalStore = useGlobalFaciesStore()

function add(): void {
  faciesGlobalStore.create({})
}
</script>
