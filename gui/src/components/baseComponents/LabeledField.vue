<template>
  <div>
    <v-label
      :id="labelId"
      :for="id"
      :text="label"
      class="mb-1 opacity-100 text-high-emphasis"
    />
    <v-defaults-provider :defaults="fieldDefaults">
      <slot :field-attrs="fieldAttrs" />
    </v-defaults-provider>
  </div>
</template>

<script setup lang="ts">
import { useId } from 'vue'

defineProps<{ label: string }>()

const id = useId()
const labelId = `${id}-label`

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
const fieldDefaults = {
  VSelect: redesignedField,
  VCombobox: redesignedField,
}
</script>
