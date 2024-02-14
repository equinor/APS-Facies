<template>
  <v-container class="text-center column wrap align">
    <v-row>
      <v-col cols="12">
        <v-select
          v-model="selected"
          :items="available"
          label="Gaussian Fields to be used"
          multiple
          variant="underlined"
        />
      </v-col>
    </v-row>
    <v-row align="center" justify="space-around">
      <v-col v-for="([field, other], index) in combinations" :key="index">
        <cross-plot
          v-if="field.simulated && other.simulated"
          :value="[field, other]"
        />
        <v-progress-circular v-else :size="70" indeterminate />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'
import { ID } from '@/utils/domain/types'

import CrossPlot from './index.vue'
import { useStore } from '../../../store'
import { ref, computed, watch, onBeforeMount } from 'vue'
import type { ListItem } from '@/utils/typing'

const props = defineProps<{ value: GaussianRandomField[] }>()
const store = useStore()

const selected = ref<ID[]>([])
const available = computed<ListItem<ID>[]>(() =>
  props.value.map((field) => ({
    value: field.id,
    title: field.name,
  })),
)

const combinations = computed<GaussianRandomField[][]>(() => {
  const pairs: GaussianRandomField[][] = []
  const available = selected.value.map(
    (id) => store.state.gaussianRandomFields.available[id],
  )
  if (!available) return pairs
  for (let i = 0; i < available.length; i++) {
    for (let j = i + 1; j < available.length; j++) {
      pairs.push([available[i], available[j]])
    }
  }
  return pairs
})

watch(
  selected,
  (value: ID[]) => {
    store.dispatch('gaussianRandomFields/updateSimulations', { fields: value })
  },
  { deep: true },
)

watch(
  available,
  (value: Item[]) => {
    if (
      selected.value.some(
        (selectedItem) =>
          !value.find((availableItem) => availableItem.value === selectedItem),
      )
    ) {
      // That is, if there is some selected value that is no longer available
      selected.value = available.value
        .filter((availableItem) =>
          selected.value.some(
            (selectedItem) => selectedItem === availableItem.value,
          ),
        )
        .map((el) => el.value)
    }
  },
  { deep: true },
)

onBeforeMount(() => {
  if (selected.value.length === 0 && props.value.length >= 2) {
    props.value.slice(0, 2).forEach((field) => selected.value.push(field.id))
  }
})
</script>
