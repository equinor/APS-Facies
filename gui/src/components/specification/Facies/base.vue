<template>
  <v-select
    :items="faciesOptions"
    v-model="selected"
    :clearable="clearable"
    variant="underlined"
  />
</template>

<script setup lang="ts">
import type Facies from '@/utils/domain/facies/local'
import type { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useFaciesStore } from '@/stores/facies'

type Props = {
  modelValue: Facies | null
  disable?: boolean | ((facies: Facies) => boolean)
  clearable?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  disable: false,
  clearable: false,
})
const emit = defineEmits<{
  (event: 'update:model-value', value: Facies | null): void
}>()

const faciesStore = useFaciesStore()

const selected = computed({
  get: () => props.modelValue,
  set: (facies: Facies | null) => emit('update:model-value', facies),
})

const faciesOptions = computed<ListItem<Facies>[]>(() => {
  return faciesStore.selected.map(
    (facies) =>
      ({
        title: facies.alias,
        value: facies,
        props: {
          disabled:
            props.disable instanceof Function
              ? props.disable(facies)
              : props.disable,
        },
      }) as ListItem<Facies>,
  )
})
</script>
