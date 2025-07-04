<template>
  <v-btn
    :disabled="disabled || waiting"
    :theme="theme"
    :color="color"
    :large="large"
    :start="left"
    :end="right"
    :small="small"
    icon
    variant="text"
    @click.stop="(e: MouseEvent) => emit('click', e)"
  >
    <v-icon
      :theme="theme"
      :color="color"
      :large="large"
      :start="left"
      :medium="medium"
      :end="right"
      :size="size"
      :small="small"
    >
      {{ fullIconName }}
    </v-icon>
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
  theme?: 'light' | 'dark'
  color?: Color
  large?: boolean
  left?: boolean
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
  theme: undefined,
  color: undefined,
  large: false,
  left: false,
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
