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

import { useStore } from '../../store'
import { computed } from 'vue'

withDefaults(defineProps<{ hideAlias?: boolean }>(), { hideAlias: false })

const store = useStore()

const current = computed(() => store.getters.facies)
const canRemove = computed(() =>
  !!current.value ? !store.getters['facies/isFromRMS'](current) : false,
)
const removeError = computed(() => {
  if (!current.value) {
    return 'A facies must be selected'
  }
  if (!canRemove.value) {
    return `The selected facies, ${current.value.name}, is from RMS, and cannot be deleted from this GUI`
  }
  return ''
})

async function add(): Promise<void> {
  await store.dispatch('facies/global/new', {})
}

async function remove(): Promise<void> {
  await store.dispatch('facies/global/removeSelectedFacies')
}
</script>
