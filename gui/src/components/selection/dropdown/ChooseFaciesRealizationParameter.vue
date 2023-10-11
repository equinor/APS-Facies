<template>
  <v-combobox
    v-model="faciesRealizationParameter"
    v-model:search-input="faciesRealizationParameter"
    :items="available"
    :append-icon="''"
    :append-outer-icon="'$vuetify.icons.values.search'"
    label="Facies Realization parameter"
    variant="underlined"
  />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useParameterRealizationStore } from '@/stores/parameters/realization'

const parameterRealizationStore = useParameterRealizationStore()

const faciesRealizationParameter = computed({
  get: () => parameterRealizationStore.selected,
  set: (value: string | null) => (parameterRealizationStore.selected = value),
})

const available = computed(() => parameterRealizationStore.available)
</script>
