<template>
  <v-select :items="faciesOptions" v-model="selected" :clearable="clearable" variant="underlined" />
</template>

<script setup lang="ts">
import { getId } from '@/utils/helpers'

import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import { ListItem } from '@/utils/typing'
import { useStore } from '../../../store'
import { computed } from 'vue'

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
const store = useStore()

const selectedFacies = computed<Facies[]>(
  () => store.getters['facies/selected'],
)
const selected = computed<ID | ID[]>(() =>
  Array.isArray(props.modelValue) ? props.modelValue.map(getId) : getId(props.modelValue),
)

const faciesOptions = computed<ListItem<string>[]>(() => {
  return selectedFacies.value.map((facies) => ({
    title: facies.alias,
    value: facies,
    props: {
      disabled:
        props.disable instanceof Function ? props.disable(facies) : props.disable,
    }
  }) as ListItem<Facies>)
})
</script>
