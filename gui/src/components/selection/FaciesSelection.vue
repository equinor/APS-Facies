<template>
  <v-row no-gutters>
    <v-row class="fill-height" justify="start">
      <v-col cols="2">
        <icon-button icon="add" @click="add" />
      </v-col>
      <v-col cols="2">
        <floating-tooltip :disabled="canRemove" trigger="hover">
          <icon-button icon="remove" :disabled="!canRemove" @click="remove" />
          <template #popper>{{ removeError }}</template>
        </floating-tooltip>
      </v-col>
      <v-col cols="8" />
    </v-row>
    <v-col cols="12">
      <facies-table :hide-alias="hideAlias" />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import FaciesTable from '@/components/table/FaciesTable/index.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'
import { useFaciesGlobalStore } from '@/stores/facies/global'
import type { GlobalFacies } from '@/utils/domain'

withDefaults(defineProps<{ hideAlias?: boolean }>(), { hideAlias: false })

const faciesStore = useFaciesStore()
const faciesGlobalStore = useFaciesGlobalStore()

const current = computed(() => faciesGlobalStore.current)
const canRemove = computed(() =>
  !!current.value ? !faciesStore.isFromRMS(current.value as GlobalFacies) : false,
)

const removeError = computed(() => {
  if (!current.value) return 'A facies must be selected'
  if (!canRemove.value)
    return `The selected facies (${current.value!.name}) is from RMS, and cannot be deleted from this GUI`
  return ''
})

async function add() {
  await faciesGlobalStore.create({})
}

function remove() {
  faciesGlobalStore.removeSelectedFacies()
}
</script>
