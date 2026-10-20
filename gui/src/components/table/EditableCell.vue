<template>
  <v-text-field
    v-model="_fieldValue"
    :type="numeric ? 'number' : 'text'"
    :error-messages="errorMessages"
    @keydown.enter="update"
    @focusout="update"
  />
</template>

<script setup lang="ts" generic="T, N extends boolean">
import { computed, onBeforeMount, ref, watch } from 'vue'

type OnSubmit = N extends true ? number : string

const props = withDefaults(
  defineProps<{
    value: T
    field: keyof T
    numeric?: N
    restrictions?: ((value: string) => string)[]
  }>(),
  {
    numeric: undefined,
    restrictions: () => [],
  },
)
const emit = defineEmits<{
  (event: 'submit', value: OnSubmit): void
  (event: 'update:error', error: boolean): void
}>()

const _fieldValue = ref('')
function reset(): void {
  _fieldValue.value = props.value[props.field] as string
}
onBeforeMount(() => reset())
watch(() => props.value[props.field], reset)

const errorMessages = computed(() =>
  props.restrictions
    .map((restriction) => restriction(_fieldValue.value))
    .filter((errorMessage) => !!errorMessage),
)

function update(): void {
  if (errorMessages.value.length > 0) return

  const value = _fieldValue.value
  if (props.numeric) {
    emit('submit', parseFloat(value) as OnSubmit)
  } else {
    emit('submit', value as OnSubmit)
  }
}
</script>
