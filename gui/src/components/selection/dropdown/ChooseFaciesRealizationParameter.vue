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
import { useStore } from '../../../store'

const store = useStore()

const faciesRealizationParameter = computed({
  get: () => store.state.parameters.realization.selected,
  set: (value: string | null) =>
    store.dispatch('parameters/realization/select', value),
})

const available = computed(() => store.state.parameters.realization.available)
</script>
