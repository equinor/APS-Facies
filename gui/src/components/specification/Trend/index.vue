<template>
  <v-col cols="12">
    <h4>Trend</h4>
    <v-row>
      <v-col cols="6">
        <v-checkbox v-model="useTrend" label="Apply trend to field" />
      </v-col>
      <v-spacer />
      <v-col cols="6">
        <relative-standard-deviation
          v-if="useTrend"
          :value="value"
          @update:error="(e: boolean) => invalid.relativeStdDev=e"
        />
      </v-col>
    </v-row>
    <v-col v-if="useTrend">
      <v-row class="fill-height" align="center" justify="center" no-gutters>
        <v-col cols="6">
          <item-selection
            v-model="trendType"
            :items="availableTrends"
            :constraints="{ required: true }"
            label="Trend type"
            @update:error="(e: boolean) => invalid.type=e"
          />
          <div v-if="hasLinearProperties">
            <depositional-azimuth-angle
              :value="value"
              @update:error="(e: boolean) => invalid.azimuth=e"
            />
            <stacking-angle-specification
              :value="value"
              @update:error="(e: boolean) => invalid.stacking=e"
            />
          </div>
          <migration-angle
            v-if="hasHyperbolicProperties"
            :value="value"
            @update:error="(e: boolean) => invalid.migration=e"
          />
        </v-col>
        <v-spacer />
        <v-col cols="5">
          <v-select
            v-if="isRmsParameter"
            v-model="trendParameter"
            :items="availableRmsTrendParameters"
            label="Trend parameter"
            variant="underlined"
          />
          <v-select
            v-if="isRmsTrendMap"
            v-model="trendMapZone"
            v-tooltip="'Select zone name from Zones folder for maps'"
            :items="availableRmsTrendZones"
            label="Zone name"
            variant="underlined"
          />
          <v-select
            v-if="isRmsTrendMap"
            v-model="trendMapName"
            v-tooltip="
              'Select surface with 2D trend corresponding to selected zone'
            "
            :items="availableRmsTrendMaps"
            :disabled="!hasDefinedRmsTrendZone"
            label="Trend map"
            variant="underlined"
          />
          <div v-if="hasEllipticProperties">
            <curvature-specification
              :value="value"
              @update:error="(e: boolean) => invalid.curvature=e"
            />
            <origin-specification
              :value="value"
              @update:error="(e: boolean) => invalid.origin=e"
            />
          </div>
          <v-col>
            <relative-size-of-ellipse
              v-if="hasEllipticConeProperties"
              :value="value"
              @update:error="(e: boolean) => invalid.relativeEllipseSize=e"
            />
          </v-col>
        </v-col>
      </v-row>
    </v-col>
  </v-col>
</template>

<script setup lang="ts">
import type { GaussianRandomField } from '@/utils/domain'
import type { TrendType } from '@/utils/domain/gaussianRandomField/trend'

import { notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import OriginSpecification from '@/components/specification/Trend/Origin/index.vue'
import {
  StackingAngleSpecification,
  CurvatureSpecification,
  DepositionalAzimuthAngle,
  MigrationAngle,
  RelativeSizeOfEllipse,
  RelativeStandardDeviation,
} from '@/components/specification/Trend/InputFields'

import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'
import { useParameterRmsTrendStore } from '@/stores/parameters/rms-trend'
import { type TrendMap, useParameterRmsTrendMapZoneStore } from '@/stores/parameters/rms-trend-map-zones'
import { ref, computed, watch } from 'vue'
import { useConstantsOptionsTrendsStore } from '@/stores/constants/options'

interface Invalid {
  relativeStdDev: boolean
  type: boolean
  azimuth: boolean
  stacking: boolean
  migration: boolean
  curvature: boolean
  origin: boolean
  relativeEllipseSize: boolean
}

const invalid = ref<Invalid>({
  relativeStdDev: false,
  type: false,
  azimuth: false,
  stacking: false,
  migration: false,
  curvature: false,
  origin: false,
  relativeEllipseSize: false,
})

const props = defineProps<{ value: GaussianRandomField }>()
const emit = defineEmits<{
  (event: 'update:error', error: boolean): void
}>()

const trend = computed(() => props.value.trend)

function notOneOf(types: TrendType[]): boolean {
  return types.indexOf(trend.value.type) === -1
}

const availableRmsTrendParameters = computed<string[]>(
  () => useParameterRmsTrendStore().available,
)
const rmsTrendMapZones = computed<TrendMap[]>(
  () => useParameterRmsTrendMapZoneStore().available,
)
const availableRmsTrendZones = computed(() =>
  rmsTrendMapZones.value
    .filter((zone) => zone.representations.length > 0)
    .map(({ name }) => name),
)

const trendMapZoneLookup = computed<Record<string, string[]>>(() => {
  return rmsTrendMapZones.value.reduce((mapping, trendMap) => {
    mapping[trendMap.name] = trendMap.representations
    return mapping
  }, {} as Record<string, string[]>)
})

const availableRmsTrendMaps = computed(() =>
  trendMapZone.value ? trendMapZoneLookup.value[trendMapZone.value] : [],
)

const availableTrends = computed<string[]>(
  () => useConstantsOptionsTrendsStore().available,
)

const hasLinearProperties = computed(
  () =>
    notEmpty(trendType.value) &&
    notOneOf(TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION),
)

const hasEllipticProperties = computed(
  () => hasLinearProperties.value && notOneOf(['LINEAR']),
)
const hasHyperbolicProperties = computed(
  () => hasEllipticProperties.value && notOneOf(['ELLIPTIC']),
)
const hasEllipticConeProperties = computed(
  () => hasHyperbolicProperties.value && notOneOf(['HYPERBOLIC']),
)

const isRmsParameter = computed(() => trend.value.type === 'RMS_PARAM')
const isRmsTrendMap = computed(() => trend.value.type === 'RMS_TRENDMAP')

const trendType = computed({
  get: () => props.value.trend.type,
  set: (value: TrendType) => {
    if (value === 'HYPERBOLIC' && props.value.trend.curvature.value <= 1) {
      // Curvature for hyperbolic trends must be strictly greater than 1
      props.value.trend.curvature.value = 1.01
    }
    props.value.trend.type = value
  },
})
const trendParameter = computed({
  get: () => props.value.trend.parameter,
  set: (value: string | null) => (props.value.trend.parameter = value),
})
const trendMapName = computed({
  get: () => props.value.trend.trendMapName,
  set: (value: string | null) => (props.value.trend.trendMapName = value),
})
const trendMapZone = computed({
  get: () => props.value.trend.trendMapZone,
  set: (value: string | null) => (props.value.trend.trendMapZone = value),
})
const useTrend = computed({
  get: () => props.value.trend.use,
  set: (value: boolean) => (props.value.trend.use = value),
})

const hasDefinedRmsTrendZone = computed(() => trendMapZone.value != null)

watch(
  invalid,
  (value: Invalid) => {
    const someInvalid = Object.values(value).some((invalid) => invalid)
    emit('update:error', useTrend.value && someInvalid)
  },
  { deep: true },
)
</script>
