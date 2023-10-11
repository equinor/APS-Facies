<template>
  <div>
    <azimuth-angle
      :value="value"
      :property-type="propertyType"
      sub-property-type="azimuth"
      value-type="azimuth"
      label="Azimuth"
      unit="°"
      use-modulus
      @update:error="(e: boolean) => update('azimuth', e)"
    />
    <dip-angle
      :value="value"
      :property-type="propertyType"
      sub-property-type="dip"
      value-type="dip"
      label="Dip"
      unit="°"
      use-modulus
      @update:error="(e: boolean) => update('dip', e)"
    />
  </div>
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'
import { ref, watch } from 'vue'
import StorableNumericField from '@/components/specification/StorableNumericField.vue'

const AzimuthAngle = StorableNumericField
const DipAngle = StorableNumericField

interface Invalid {
  azimuth: boolean
  dip: boolean
}

type Props = { value: GaussianRandomField }
defineProps<Props>()

const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const invalid = ref<Invalid>({
  azimuth: false,
  dip: false,
})

const propertyType = 'angle'

watch(
  invalid,
  () => {
    emit('update:error', invalid.value.azimuth || invalid.value.dip)
  },
  { deep: true },
)

function update(type: 'dip' | 'azimuth', value: boolean): void {
  invalid.value[type] = value
}
</script>
