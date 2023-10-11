<template>
  <base-dropdown
    v-if="isShown"
    v-model="selected"
    :items="available"
    :label="label"
    :disabled="isDisabled"
    :warn="warn"
    :warn-even-when-empty="warnEvenWhenEmpty"
    :warn-message="warnMessage"
  />
</template>

<script setup lang="ts">
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'

import { ListItem } from '@/utils/typing'
import { computed } from 'vue'
import { useStore } from '../../../store'

type Props = {
  label: string
  parameterType: string
  hideIfDisabled?: boolean
  disabled?: boolean
  regular?: boolean
  warn?: boolean
  warnMessage?: string
  warnEvenWhenEmpty?: boolean
}
const props = withDefaults(defineProps<Props>(), {
  hideIfDisabled: true,
  disabled: false,
  regular: false,
  warn: false,
  warnMessage: '',
  warnEvenWhenEmpty: false,
})
const store = useStore()
const available = computed<ListItem<string>[]>(() =>
  store.state.parameters[props.parameterType].available.map(
    (item: string): ListItem<string> => ({
      title: item,
      value: item,
    }),
  ),
)

const isDisabled = computed(
  () =>
    (!props.regular && available.value ? available.value.length <= 1 : false) ||
    props.disabled,
)
const isShown = computed(() => !(props.hideIfDisabled && isDisabled.value))
const selected = computed({
  get: () => store.state.parameters[props.parameterType].selected,
  set: (value: string) =>
    store.dispatch(`parameters/${props.parameterType}/select`, value),
})
</script>
