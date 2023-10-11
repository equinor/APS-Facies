<template>
  <div>
    Origin
    <v-row class="fill-height" align="center" justify="center">
      <v-col :class="coordinateClass">
        <origin-x
          :value="value"
          :origin-type="originType"
          coordinate-axis="x"
          @update:error="(e: boolean) => invalid.x = e"
        />
      </v-col>
      <v-col :class="coordinateClass">
        <origin-y
          :value="value"
          :origin-type="originType"
          coordinate-axis="y"
          @update:error="(e: boolean) => invalid.y = e"
        />
      </v-col>
      <v-col v-if="!isEllipticCone" :class="coordinateClass">
        <origin-z
          :value="value"
          :origin-type="originType"
          coordinate-axis="z"
          @update:error="(e: boolean) => invalid.z = e"
        />
      </v-col>
    </v-row>
    <v-select
      v-model="originType"
      :items="availableOriginTypes"
      label="Origin type"
    />
  </div>
</template>

<script setup lang="ts">
import { GaussianRandomField } from '@/utils/domain'
import { OriginType } from '@/utils/domain/gaussianRandomField/trend'
import OriginCoordinate from './Coordinate.vue'
import { ref, computed, watch } from 'vue'
import { useStore } from '../../../../store'

const OriginX = OriginCoordinate
const OriginY = OriginCoordinate
const OriginZ = OriginCoordinate

const coordinateClass = 'pa-1 pt-2'

interface Invalid {
  x: boolean
  y: boolean
  z: boolean
}

const props = defineProps<{ value: GaussianRandomField }>()
const store = useStore()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const invalid = ref<Invalid>({
  x: false,
  y: false,
  z: false,
})

const availableOriginTypes = computed(
  () => store.state.constants.options.origin.available,
)
const trend = computed(() => props.value.trend)
const isEllipticCone = computed(() => trend.value.type === 'ELLIPTIC_CONE')
const originType = computed({
  get: () => trend.value.origin.type,
  set: (value: OriginType) =>
    store.dispatch('gaussianRandomFields/originType', {
      field: props.value,
      value,
    }),
})

watch(invalid, ({ x, y, z }: Invalid) =>
  emit('update:error', x || y || (!isEllipticCone.value && z)),
)
</script>
