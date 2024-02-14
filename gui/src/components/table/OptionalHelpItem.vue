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

interface MaybeHelpText {
  help?: string
}

interface Text extends MaybeHelpText {
  text: string
  [_: string]: any
}

interface Named extends MaybeHelpText {
  name: string
  [_: string]: any
}
type Value = Text | Named | string | number
const props = defineProps<{ value: Value }>()

const text = computed(() => {
  if (typeof props.value === 'string') return props.value
  if (typeof props.value === 'number') return props.value.toString()
  // Text or Named
  return props.value.text ?? props.value.name
})

const helpText = computed(() => {
  // string or number
  if (typeof props.value !== 'object') return ''
  return props.value.help
})

const hasHelp = computed(() => notEmpty(helpText.value))
</script>
