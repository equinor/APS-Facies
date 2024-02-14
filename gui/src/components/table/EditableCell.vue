<template>
  <div>
    <!-- <v-edit-dialog lazy @open="reset"> -->
    <v-text-field
      slot="input"
      v-model="_fieldValue"
      :label="label"
      :type="numeric ? 'number' : 'text'"
      :error-messages="errorMessages"
      single-line
      @keydown.enter="update"
      @focusout="update"
      @update:error="(e: boolean) => emit('update:error', e)"
      hide-details
      variant="underlined"
    />
    <!-- </v-edit-dialog> -->
  </div>
</template>

<script setup lang="ts" generic="T, N extends boolean">
import { computed, onBeforeMount, ref } from 'vue'

type OnSubmit = N extends true
  ? number
  : string

const props = withDefaults(defineProps<{
  value: T
  field: keyof T
  label?: string
  numeric?: N
  restrictions?: ((value: string) => string)[]
}>(), {
  label: 'Edit',
  numeric: undefined,
  restrictions: () => [],
})
const emit = defineEmits<{
  (event: 'submit', value: OnSubmit): void
  (event: 'update:error', error: boolean): void
}>()

const _fieldValue = ref('')
function reset(): void {
  _fieldValue.value = props.value[props.field] as string
}
onBeforeMount(() => reset())

const errorMessages = computed(() =>
  props.restrictions
    .map((restriction) => restriction(_fieldValue.value))
    .filter((errorMessage) => !!errorMessage),
)

function update(): void {
  if (errorMessages.value.length > 0) return

  const value = _fieldValue.value
  emit('submit', {
    ...props.value,
    [props.field]: props.numeric ? Number(value) : value,
  })
}
</script>
