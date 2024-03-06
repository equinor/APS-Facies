<template>
  <wait-btn
    :title="title"
    :outlined="outline"
    :disabled="disabled"
    :tooltip-text="tooltipText"
    color="primary"
    @click="(e: MouseEvent) => emit('click', e)"
  />
</template>

<script setup lang="ts">
import WaitBtn from '@/components/baseComponents/WaitButton.vue'

type Props = {
  title: string
  outline?: boolean
  disabled?: boolean
  tooltipText?: string
}

withDefaults(defineProps<Props>(), {
  outline: false,
  disabled: false,
  tooltipText: '',
})

const emit = defineEmits<{
  (event: 'click', value: MouseEvent): void
}>()
</script>
