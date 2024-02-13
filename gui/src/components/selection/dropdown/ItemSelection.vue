<template>
  <v-select
    :model-value="props.modelValue"
    :items="items"
    :label="label"
    :error-messages="errors"
    variant="underlined"
    @blur="v.$touch()"
    @update:model-value="(e) => $emit('update:model-value', e as T)"
  />
</template>

<script setup lang="ts" generic="T">
import { computed, watch } from 'vue'
import { useVuelidate } from '@vuelidate/core'
import { requiredIf } from '@vuelidate/validators'
import { useInvalidation } from '@/utils/invalidation'
import type { ListItem } from '@/utils/typing'

// TODO: Consider if it should be "items: T[] | ListItem<T>[]"".
type Props = {
  modelValue: T
  items: T[] | ListItem<T>[]
  constraints: { required: boolean }
  label?: string
}
const props = withDefaults(defineProps<Props>(), { label: '' })

const emit = defineEmits<{
  (event: 'update:model-value', value: T): void
  (event: 'update:error', error: boolean): void
}>()

const vuelidateRules = computed(() => ({
  modelValue: {
    required: requiredIf(props.constraints.required),
    legalChoice: (value: T) => props.items.includes(value),
  },
}))
const v = useVuelidate(vuelidateRules, props)
useInvalidation(v)

const errors = computed(() => {
  if (!v.value) return []

  const errors: string[] = []
  if (!v.value.$dirty) return errors
  !v.value.modelValue.required && errors.push('Is required')
  !v.value.modelValue.legalChoice && errors.push('Illegal choice')
  return errors
})

watch(v, () => {
  emit('update:error', v.value.$invalid)
})
</script>
