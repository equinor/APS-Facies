<template>
  <div>
    <main-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="main"
      label="Parallel to Azimuth"
      unit="m"
      strictly-greater
      @update:error="(e: boolean) => invalid.main = e"
    />
    <perpendicular-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="perpendicular"
      label="Normal to Azimuth"
      unit="m"
      strictly-greater
      @update:error="(e: boolean) => invalid.perpendicular = e"
    />
    <vertical-range
      :value="value"
      :property-type="propertyType"
      sub-property-type="vertical"
      label="Vertical (normal to dip)"
      unit="m"
      strictly-greater
      @update:error="(e: boolean) => invalid.vertical = e"
    />
  </div>
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'

import { ref, watch } from 'vue'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'

const MainRange = StorableNumericField
const PerpendicularRange = StorableNumericField
const VerticalRange = StorableNumericField

type Props = { value: GaussianRandomField }
defineProps<Props>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

interface Invalid {
  main: boolean
  perpendicular: boolean
  vertical: boolean
}
const invalid = ref<Invalid>({
  main: false,
  perpendicular: false,
  vertical: false,
})

const propertyType = 'range'

watch(invalid, ({ vertical, perpendicular, main }) => {
  emit('update:error', vertical || perpendicular || main)
})
</script>
