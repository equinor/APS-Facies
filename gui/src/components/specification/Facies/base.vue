<template>
  <v-select
    :items="faciesOptions"
    :value="selected"
    :clearable="clearable"
    @input.capture="(facies: Value) => $emit('input', facies)"
  />
</template>

<script setup lang="ts">
import { getId } from '@/utils/helpers'

import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import { ListItem } from '@/utils/typing'
import { useStore } from '../../../store'
import { computed } from 'vue'

type Value = Facies | ID | Facies[] | ID[]

type Props = {
  value: Value
  disable: boolean | ((facies: Facies) => boolean)
  clearable: boolean
}
const props = withDefaults(defineProps<Props>(), {
  disable: false,
  clearable: false,
})
const store = useStore()

const selectedFacies = computed<Facies[]>(
  () => store.getters['facies/selected'],
)
const selected = computed<ID | ID[]>(() =>
  Array.isArray(props.value) ? props.value.map(getId) : getId(props.value),
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
