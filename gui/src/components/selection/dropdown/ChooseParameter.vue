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
    :loading="store.loading"
  />
</template>

<script setup lang="ts">
import BaseDropdown from '@/components/selection/dropdown/BaseDropdown.vue'

import { computed } from 'vue'
import { useParameterRegionStore } from '@/stores/parameters/region'
import { useParameterBlockedWellStore } from '@/stores/parameters/blocked-well'
import { useParameterBlockedWellLogStore } from '@/stores/parameters/blocked-well-log'
import type { ParameterType } from '@/utils/domain/types'

type Props = {
  label: string
  parameterType: ParameterType
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

const store = computed(() => {
  switch (props.parameterType) {
    case 'region':
      return useParameterRegionStore()
    case 'blockedWell':
      return useParameterBlockedWellStore()
    case 'blockedWellLog':
      return useParameterBlockedWellLogStore()
  }
})

const available = computed(() =>
  store.value.available.map((item) => ({ title: item, value: item })),
)

const isDisabled = computed(
  () =>
    (!props.regular && available.value ? available.value.length <= 1 : false) ||
    props.disabled,
)
const isShown = computed(() => !(props.hideIfDisabled && isDisabled.value))
const selected = computed({
  get: () => store.value.selected!,
  set: (value: string) => store.value.select(value),
})
</script>
