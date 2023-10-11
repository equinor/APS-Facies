<template>
  <v-edit-dialog lazy @open="reset">
    {{ value[field] }}
    <v-text-field
      slot="input"
      v-model="_fieldValue"
      :label="label"
      :type="numeric ? 'number' : 'text'"
      :error-messages="errorMessages"
      single-line
      @keydown.enter="submit"
      @update:error="(e: boolean) => emit('update:error', e)"
    />
  </v-edit-dialog>
</template>

<script setup lang="ts" generic="T">
import { computed } from 'vue'
import { onBeforeMount } from 'vue'
import { ref } from 'vue'

type Props = {
  value: T
  field: string
  label: string
  numeric: boolean
  restrictions: ((value: string) => string)[]
}
const props = withDefaults(defineProps<Props>(), {
  label: 'Edit',
  numeric: false,
  restrictions: () => [],
})
const emit = defineEmits<{
  (event: 'submit', value: T & { [key: string]: number | string }): void
  (event: 'update:error', error: boolean): void
}>()

const _fieldValue = ref('')
function reset(): void {
  _fieldValue.value = props.value[props.field]
}
onBeforeMount(() => reset())

const errorMessages = computed(() =>
  props.restrictions
    .map((restriction) => restriction(_fieldValue.value))
    .filter((errorMessage) => !!errorMessage),
)

function submit(): void {
  if (errorMessages.value.length > 0) return

  const value = _fieldValue.value
  emit('submit', {
    ...props.value,
    [props.field]: props.numeric ? Number(value) : value,
  })
}
</script>
