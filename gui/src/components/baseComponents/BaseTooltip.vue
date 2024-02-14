<template>
  <floating-tooltip
    :triggers="trigger === 'manual' ? [] : [trigger]"
    :disabled="!_message || disabled"
    :shown="_open"
    placement="bottom"
  >
    <slot />
    <template #popper>{{ _message }}</template>
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
