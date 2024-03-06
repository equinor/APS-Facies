<template>
  <v-row>
    <v-col cols="1">
      <v-checkbox v-model="enabled" :disabled="disabled" />
    </v-col>
    <v-col>
      <file-selection
        v-model="path"
        :label="label"
        :disabled="!enabled || disabled"
        :relative-to="relativeTo"
        @update:error="(e) => propagateError(e)"
      />
    </v-col>
  </v-row>
</template>
<script setup lang="ts">
import FileSelection from './FileSelection.vue'
import { computed } from 'vue'

interface State {
  path: string
  disabled: boolean
}

type Props = {
  modelValue: State
  label: string
  disabled?: boolean
  relativeTo?: string
}
const props = withDefaults(defineProps<Props>(), { disabled: true })
const emit = defineEmits<{
  (event: 'update:model-value', value: State): void
  (event: 'update:error', error: boolean): void
}>()

const path = computed({
  get: () => props.modelValue.path,
  set: (path: string) =>
    emit('update:model-value', { ...props.modelValue, path }),
})
const enabled = computed({
  get: () => !props.modelValue.disabled,
  set: (enabled: boolean) =>
    emit('update:model-value', { ...props.modelValue, disabled: !enabled }),
})

function propagateError(error: boolean): void {
  emit('update:error', error)
}
</script>
