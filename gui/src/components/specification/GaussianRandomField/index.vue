<template>
  <v-row no-gutters>
    <v-col cols="6">
      <gaussian-plot :value="value" expand />
    </v-col>
    <v-col cols="1" />
    <v-col cols="5">
      <h4>Variogram selection</h4>
      <item-selection
        v-model="variogramType"
        :items="availableVariograms"
        :constraints="{ required: true }"
        label="Variogram"
      />
      <icon-button
        :disabled="!canSimulate"
        icon="random"
        @click="() => updateSimulation(true)"
      />
      <icon-button
        :disabled="!canSimulate"
        :waiting="waitingForSimulation"
        icon="refresh"
        @click="() => updateSimulation(false)"
      />
      <icon-button icon="settings" @click="openVisualizationSettings" />
      <visualization-settings-dialog ref="visualisationSettingsDialog" />
    </v-col>
    <!--New line-->
    <v-col class="column" align-self="start" cols="6">
      <h4>Anisotropy direction</h4>
      <anisotropy-direction
        :value="value"
        @update:error="(e: boolean) => updateInvalid('anisotropyDirection', e)"
      />
      <power-specification
        v-if="isGeneralExponential"
        :value="value"
        @update:error="(e: boolean) => updateInvalid('power', e)"
      />
    </v-col>
    <v-col cols="1" />
    <v-col cols="5">
      <h4>Ranges</h4>
      <range-specification
        :value="value"
        @update:error="(e: boolean) => updateInvalid('range', e)"
      />
    </v-col>
    <!--New line-->
    <v-row>
      <trend-specification
        :value="value"
        @update:error="(e: boolean) => updateInvalid('trend', e)"
      />
    </v-row>
  </v-row>
</template>

<script setup lang="ts">
import cloneDeep from 'lodash/cloneDeep'

import { isDevelopmentBuild, TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'

import { notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import GaussianPlot from '@/components/plot/GaussianPlot/index.vue'
import TrendSpecification from '@/components/specification/Trend/index.vue'
import RangeSpecification from '@/components/specification/GaussianRandomField/Range.vue'
import AnisotropyDirection from '@/components/specification/GaussianRandomField/AnisotropyDirection.vue'
import PowerSpecification from '@/components/specification/GaussianRandomField/Power.vue'
import VisualizationSettingsDialog from '@/components/specification/GaussianRandomField/VisualizationSettingsDialog.vue'
import IconButton from '@/components/selection/IconButton.vue'

import type Field from '@/utils/domain/gaussianRandomField'
import { ref, computed, onBeforeMount, watch } from 'vue'
import { useConstantsOptionsVariogramsStore } from '@/stores/constants/options'
import { useGaussianRandomFieldStore } from '@/stores/gaussian-random-fields'
import { provideInvalidation } from '@/utils/invalidation'

interface Invalid {
  anisotropyDirection: boolean
  power: boolean
  range: boolean
  trend: boolean
}

type Props = { value: Field }
const props = defineProps<Props>()

const fieldStore = useGaussianRandomFieldStore()
const { invalidate } = provideInvalidation()

const waitingForSimulation = ref(false)
const visualisationSettingsDialog = ref<InstanceType<
  typeof VisualizationSettingsDialog
> | null>(null)
const invalid = ref<Invalid>({
  anisotropyDirection: false,
  power: false,
  range: false,
  trend: false,
})

const availableVariograms = computed(
  () => useConstantsOptionsVariogramsStore().available,
)

const isGeneralExponential = computed(
  () => variogramType.value === 'GENERAL_EXPONENTIAL',
)

const variogram = computed(() => props.value.variogram)
const variogramType = computed({
  get: () => variogram.value.type,
  set: (value: string) => (props.value.variogram.type = value),
})

const trend = computed(() => props.value.trend)
const isValid = computed(() =>
  Object.values(invalid.value).every((invalid) => !invalid),
)

const canSimulate = computed(
  () =>
    notEmpty(variogramType.value) &&
    (trend.value.use
      ? TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION.indexOf(
          trend.value.type,
        ) === -1
      : true) &&
    isValid.value &&
    !waitingForSimulation.value,
)

onBeforeMount(() => {
  if (!props.value.isRepresentative) {
    updateSimulation()
  }
})

async function simulation(renew = false): Promise<void> {
  if (renew) fieldStore.newSeed(props.value)
  await fieldStore.updateSimulation(props.value)
}

async function updateSimulation(renew = false): Promise<void> {
  waitingForSimulation.value = true
  try {
    await simulation(renew)
  } catch (reason) {
    if (isDevelopmentBuild()) console.error(reason)
    invalidate()
  } finally {
    waitingForSimulation.value = false
  }
}

async function openVisualizationSettings(): Promise<void> {
  if (!visualisationSettingsDialog.value) {
    console.error("Could not open Visualization Settings, as Dialog component was not mounted.")
    return
  }
  const { save, settings } = await visualisationSettingsDialog.value.open(
    cloneDeep(props.value.settings),
  )
  if (save) {
    props.value.settings = settings
    await updateSimulation()
  }
}

function updateInvalid(type: keyof Invalid, value: boolean): void {
  invalid.value[type] = value
}

watch(isValid, async (value: boolean) => {
  props.value.valid = value
})
</script>
