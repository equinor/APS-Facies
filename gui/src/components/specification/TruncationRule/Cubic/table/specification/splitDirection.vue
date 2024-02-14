<template>
  <v-radio-group v-model="splitDirection" label="Split direction">
    <v-radio :label="'Vertical'" value="V" />
    <v-radio :label="'Horizontal'" value="H" />
  </v-radio-group>
</template>

<script setup lang="ts">
import { Cubic } from '@/utils/domain'
import { useStore } from '../../../../../../store'
import { computed } from 'vue'
import type { OrientationString } from '@/utils/domain/truncationRule/cubic/direction'

const props = defineProps<{ value: Cubic }>()
const store = useStore()

const splitDirection = computed<OrientationString>({
  get: () => props.value.direction.specification,
  set: (value: OrientationString) =>
    store.dispatch('truncationRules/changeDirection', {
      rule: props.value,
      value,
    }),
})
</script>
