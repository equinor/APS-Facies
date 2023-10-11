<template>
  <div>
    <stacking-angle
      :value="value"
      @update:error="(e: boolean) => invalid.angle =e"
    />
    <item-selection
      v-model="stackingDirection"
      :items="availableStackingDirection"
      :constraints="{ required: true }"
      label="Stacking direction"
      @update:error="(e: boolean) => invalid.type =e"
    />
  </div>
</template>

<script setup lang="ts">
import type { GaussianRandomField } from '@/utils/domain'
import type { StackingDirectionType } from '@/utils/domain/gaussianRandomField/trend'

import StackingAngle from './StackingAngle.vue'
import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import { ref, computed, watch } from 'vue'
import { useConstantsOptionsStackingStore } from '@/stores/constants/options'

interface Invalid {
  angle: boolean
  type: boolean
}

const props = defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const invalid = ref<Invalid>({
  angle: false,
  type: false,
})

const availableStackingDirection = computed(
  () => useConstantsOptionsStackingStore().available,
)

const stackingDirection = computed({
  get: () => props.value.trend.stackingDirection,
  set: (value: StackingDirectionType) =>
    (props.value.trend.stackingDirection = value),
})

watch(
  invalid,
  ({ angle, type }: Invalid) => emit('update:error', angle || type),
  { deep: true },
)
</script>
