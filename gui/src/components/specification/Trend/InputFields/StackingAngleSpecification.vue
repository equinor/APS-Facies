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
import { GaussianRandomField } from '@/utils/domain'
import { StackingDirectionType } from '@/utils/domain/gaussianRandomField/trend'

import StackingAngle from './StackingAngle.vue'
import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import { ref, computed, watch } from 'vue'
import { useStore } from '../../../../store'

interface Invalid {
  angle: boolean
  type: boolean
}

const props = defineProps<{ value: GaussianRandomField }>()
const store = useStore()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const invalid = ref<Invalid>({
  angle: false,
  type: false,
})

const availableStackingDirection = computed(
  () => store.state.constants.options.stacking.available,
)

const trend = computed(() => props.value.trend)
const stackingDirection = computed({
  get: () => trend.value.stackingDirection,
  set: (value: StackingDirectionType) =>
    store.dispatch('gaussianRandomFields/stackingDirection', {
      field: props.value,
      value,
    }),
})

watch(
  invalid,
  ({ angle, type }: Invalid) => emit('update:error', angle || type),
  { deep: true },
)
</script>
