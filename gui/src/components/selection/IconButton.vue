<template>
  <v-btn
    :disabled="disabled || waiting"
    :color="color"
    :dark="dark"
    :large="large"
    :start="left"
    :end="right"
    :light="light"
    :small="small"
    icon
    variant="text"
    @click.stop="(e: MouseEvent) => emit('click', e)"
  >
    <v-icon
      :color="color"
      :dark="dark"
      :large="large"
      :left="left"
      :light="light"
      :medium="medium"
      :right="right"
      :size="size"
      :small="small"
      :x-large="xLarge"
      >{{ fullIconName }}</v-icon
    >
  </v-btn>
</template>

<script setup lang="ts">
import type { Color } from '@/utils/domain/facies/helpers/colors'
import { computed } from 'vue'

type Props = {
  icon: string
  waiting?: boolean
  disabled?: boolean
  loadingSpinner?: boolean
  color?: Color
  dark?: boolean
  large?: boolean
  left?: boolean
  light?: boolean
  medium?: boolean
  right?: boolean
  size?: number | string
  small?: boolean
  xLarge?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  waiting: false,
  disabled: false,
  loadingSpinner: false,
  color: undefined,
  dark: false,
  large: false,
  left: false,
  light: false,
  medium: false,
  right: false,
  size: undefined,
  small: false,
  xLarge: false,
})

const emit = defineEmits<{
  (event: 'click', value: MouseEvent): void
}>()

const fullIconName = computed(() => {
  if (props.loadingSpinner && props.waiting) {
    return '$refreshSpinner'
  } else {
    return `$${props.icon}${props.waiting ? 'Spinner' : ''}`
  }
})
</script>
