<template>
  <v-text-field
    v-model="fieldName"
    :error-messages="errors"
    @click.stop
    @input="$v.fieldName.$touch()"
    @blur="$v.fieldName.$touch()"
    variant="underlined"
  />
</template>
<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'
import { Optional } from '@/utils/typing'
import { ref, computed, watch, onMounted } from 'vue'
import { useStore } from '../../../store'
import useVuelidate from '@vuelidate/core'
import { required } from '@vuelidate/validators'
import { useInvalidation } from '@/utils/invalidation'

type Props = { value: GaussianRandomField }
const props = defineProps<Props>()
const store = useStore()

const fieldName = ref<Optional<string>>(null)

const fields = computed<GaussianRandomField[]>(() => store.getters.fields)
const name = computed(() => props.value.name)

const validators = {
  fieldName: {
    required,
    isUnique: (value: Optional<string>) => {
      const current = props.value.id
      return !fields.value.some(
        ({ name, id }: GaussianRandomField) => name === value && id !== current,
      )
    },
  },
}
const v = useVuelidate(validators, { fieldName })
useInvalidation(v)

const errors = computed(() => {
  if (!v.value.fieldName) return []

  const errors: string[] = []
  if (!v.value.fieldName.$dirty) return errors
  !v.value.fieldName.required && errors.push('Is required')
  !v.value.fieldName.isUnique && errors.push('Must be unique')
  return errors
})

watch(fieldName, (value: Optional<string>) => {
  if (value && v.value.fieldName && !v.value.fieldName.$invalid) {
    store.dispatch('gaussianRandomFields/changeName', {
      field: props.value,
      name: value,
    })
  }
})

onMounted(() => {
  fieldName.value = name.value
})
</script>
