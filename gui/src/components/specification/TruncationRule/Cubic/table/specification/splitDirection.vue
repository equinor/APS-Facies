<template>
  <v-radio-group v-model="splitDirection" label="Split direction">
    <v-radio :label="'Vertical'" value="V" />
    <v-radio :label="'Horizontal'" value="H" />
  </v-radio-group>
</template>

<script setup lang="ts">
import { type Cubic, Direction } from '@/utils/domain'
import { computed } from 'vue'
import type { OrientationString } from '@/utils/domain/truncationRule/cubic/direction'

const props = defineProps<{ value: Cubic }>()

const splitDirection = computed<OrientationString>({
  get: () => props.value.direction.specification,
  set: (value: OrientationString) =>
    (props.value.direction = new Direction(value)),
})
</script>
