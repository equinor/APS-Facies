<template>
  <v-row no-gutters>
    <v-col class="pa-2" cols="12">
      <v-textarea
        v-model="path"
        auto-grow
        rows="1"
        :disabled="disabled"
        :label="label"
        :append-outer-icon="icon"
        :error-messages="errors"
        @keydown.enter.prevent="() => null /** Ignore newline */"
        @click:append-outer="choosePath"
        @input="touch()"
        @blur="touch()"
        variant="underlined"
      />
    </v-col>
  </v-row>
</template>

<script setup lang="ts">
import rms from '@/api/rms'
import { relativeTo } from '@/utils/queries'
import { ref, computed, onMounted, watch } from 'vue'
import useVuelidate from '@vuelidate/core'
import { required, helpers } from '@vuelidate/validators'
import { useInvalidation } from '@/utils/invalidation'

type Props = {
  modelValue: string | null
  label: string
  disabled?: boolean
  directory?: boolean
  relativeTo?: string
}
const props = withDefaults(defineProps<Props>(), {
  disabled: false,
  directory: false,
  relativeTo: undefined,
})
const emit = defineEmits<{
  (event: 'update:model-value', value: string | null): void
  (event: 'update:error', error: boolean): void
}>()

const open = ref(false)

const path = computed({
  get: () =>
    props.relativeTo && props.modelValue
      ? relativeTo(props.relativeTo, props.modelValue)
      : props.modelValue,
  set: (value: string | null) => {
    if (props.relativeTo && !value?.startsWith('/')) {
      value = `${props.relativeTo}/${value}`
    }
    emit('update:model-value', value)
  },
})

const v = useVuelidate({
  path: {
    required,
    exists: helpers.withAsync(
      async (path: string) => {
        return await rms.exists(
          btoa(props.relativeTo ? `${props.relativeTo}/${path}` : path),
          !props.directory,
        )
      },
    ),
  }
}, {
  props,
  path,
})
useInvalidation(v)

const errors = computed(() => {
  const errors: string[] = []
  if (!v.value.path?.$dirty) return errors
  if (!v.value.path.required) {
    errors.push('Is required')
  }
  if (v.value.path.exists.$invalid) {
    errors.push('Directory does not exist')
  }
  return errors
})

const icon = computed(
  () => `$vuetify.icons.values.${open.value ? 'openFolder' : 'folder'}`,
)

async function choosePath(): Promise<void> {
  open.value = true
  let newPath = null
  try {
    newPath = props.directory
      ? await rms.chooseDir('load')
      : // setting parameters filter and suggestion does not seem to work...
        await rms.chooseFile('save', '', '')
  } catch {}
  if (newPath) {
    path.value = newPath
  }
  open.value = false
}

function touch(): void {
  v.value.path?.$touch()
}

onMounted(() => {
  if (path.value) {
    touch()
    emit('update:error', !!v.value.$invalid)
  }
})

watch(errors, (errors) => emit('update:error', errors.length > 0))
</script>
