<template>
  <div :class="{ 'd-flex align-center ga-3': inline }">
    <v-label
      :id="labelId"
      :for="id"
      :text="label"
      class="opacity-100 text-high-emphasis"
      :class="inline ? 'flex-shrink-0' : 'mb-1'"
    />
    <v-defaults-provider :defaults="fieldDefaults">
      <slot :field-attrs="fieldAttrs" />
    </v-defaults-provider>
  </div>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'

const props = withDefaults(
  defineProps<{
    label: string
    position?: 'top' | 'start'
  }>(),
  { position: 'top' },
)

const id = useId()
const labelId = `${id}-label`
const inline = computed(() => props.position === 'start')

// 'v-select' labels its input 'Open' / 'Close', for the menu it toggles, which
// would otherwise become the accessible name of the field. 'aria-labelledby'
// takes precedence over that, so the visible label is announced instead
const fieldAttrs = {
  id,
  'aria-labelledby': labelId,
}

// Once every component has been redesigned, this can be moved to 'defaults'
const redesignedField = {
  variant: 'outlined',
  rounded: 'lg',
  density: 'compact',
  hideDetails: 'auto',
}
const fieldDefaults = computed(() => {
  const field = inline.value
    ? { ...redesignedField, class: 'flex-grow-1' }
    : redesignedField
  return { VSelect: field, VCombobox: field }
})
</script>

<style lang="scss" scoped>
:deep(.v-field) {
  --v-input-control-height: 32px;
  --v-field-input-padding-top: 4px;
  --v-field-input-padding-bottom: 4px;
}
</style>
