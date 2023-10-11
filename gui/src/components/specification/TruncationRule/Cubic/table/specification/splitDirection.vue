<template>
  <v-radio-group v-model="splitDirection" label="Split direction">
    <v-radio v-for="i in [0, 1]" :key="i" :label="labels[i]" :value="i" />
  </v-radio-group>
</template>

<script setup lang="ts">
import { Cubic } from '@/utils/domain'
import { useStore } from '../../../../../../store'
import { computed } from 'vue'

const props = defineProps<{ value: Cubic }>()
const store = useStore()

const splitDirection = computed<0 | 1>({
  get: () => props.value.direction.toInteger(),
  set: (value: 0 | 1) =>
    store.dispatch('truncationRules/changeDirection', {
      rule: props.value,
      value,
    }),
})

const labels = {
  0: 'Vertical',
  1: 'Horizontal',
}
</script>
