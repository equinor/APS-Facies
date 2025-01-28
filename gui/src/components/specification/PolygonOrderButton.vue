<template>
  <floating-tooltip>
    <v-btn
      :disabled="disabled"
      :aria-label="help"
      :icon="icon"
      size="small"
      density="compact"
      variant="text"
      @click="() => emit('click')"
    />
    <template #popper>{{ help }}</template>
  </floating-tooltip>
</template>

<script setup lang="ts">
defineProps<{
  disabled: boolean
  help: string
  icon: string
}>()

const emit = defineEmits<{
  (event: 'click'): void
}>()
</script>
