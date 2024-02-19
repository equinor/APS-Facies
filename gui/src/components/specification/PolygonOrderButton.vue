<template>
  <v-btn
    :disabled="disabled"
    :icon="icon"
    size="small"
    density="compact"
    variant="text"
    @click="() => emit('click')"
  />
</template>

<script setup lang="ts">
defineProps<{
  disabled: boolean
  icon: string
}>()

const emit = defineEmits<{
  (event: 'click'): void
}>()
</script>
