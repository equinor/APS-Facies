<template>
  <floating-tooltip
    :triggers="[trigger]"
    :disabled="!_message || disabled"
    :open="_open"
  >
    <slot />
    <template #popper v-html="_message" />
  </floating-tooltip>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type Props = {
  message?: string
  trigger?: 'hover' | 'manual'
  disabled?: boolean
  open?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  message: '',
  trigger: 'hover',
  disabled: false,
  open: false,
})

const _open = computed(() => {
  return props.trigger === 'manual' ? props.open : undefined
})
const _message = computed(() => {
  return props.message || undefined
})
</script>
