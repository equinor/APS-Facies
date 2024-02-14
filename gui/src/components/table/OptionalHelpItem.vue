<template>
  <v-tooltip v-if="hasHelp" location="bottom">
    <template #activator="{ props }">
      <span v-bind="props">{{ text }}</span>
    </template>
    <span>
      {{ helpText }}
    </span>
  </v-tooltip>
  <span v-else>
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { notEmpty } from '@/utils'
import { computed } from 'vue'

const props = defineProps<{
  value: ({
    help?: string
  } & ({
    text: string
  } | {
    name: string
  })) | string | number | undefined
}>()

const text = computed<string>(() => {
  if (props.value === undefined) return ''
  if (typeof props.value === 'string') return props.value
  if (typeof props.value === 'number') return props.value.toString()
  // Text or Named
  return 'text' in props.value ? props.value.text : props.value.name
})

const helpText = computed(() => {
  // string or number
  if (typeof props.value !== 'object') return ''
  return props.value.help
})

const hasHelp = computed(() => notEmpty(helpText.value))
</script>
