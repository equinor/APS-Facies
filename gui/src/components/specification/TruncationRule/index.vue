<template>
  <truncation-header />
  <div v-if="rule">
    <v-row no-gutters>
      <v-col v-if="notBayfill" cols="12">
        <floating-tooltip :disabled="canUseOverlay" trigger="hover">
          <v-checkbox
            v-model="useOverlay"
            :disabled="!canUseOverlay"
            class="tooltip-target"
            label="Include Overlay Facies"
          />
          <template #popper>{{ useOverlayTooltip }}</template>
        </floating-tooltip>
      </v-col>
    </v-row>
    <v-row no-gutters>
      <v-col cols="12">
        <component
          :is="truncationRuleComponent"
          v-if="truncationRuleComponent && rule"
          :value="rule"
        />
      </v-col>
    </v-row>
    <v-row v-if="useOverlay" no-gutters>
      <v-col cols="12">
        <overlay-facies :value="rule as InstantiatedOverlayTruncationRule" />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import BayfillSpecification from '@/components/specification/TruncationRule/Bayfill/index.vue'
import NonCubicSpecification from '@/components/specification/TruncationRule/NonCubic/index.vue'
import CubicSpecification from '@/components/specification/TruncationRule/Cubic/index.vue'
import TruncationHeader from '@/components/specification/TruncationRule/header.vue'
import OverlayFacies from '@/components/specification/TruncationRule/Overlay/index.vue'

import { Bayfill, type InstantiatedOverlayTruncationRule } from '@/utils/domain'
import type { Optional } from '@/utils/typing'
import type { TruncationRuleType } from '@/utils/domain/truncationRule/base'
import { computed } from 'vue'
import type { Component } from 'vue'
import { useTruncationRuleStore } from '@/stores/truncation-rules'
import { useTruncationRulePresetStore } from '@/stores/truncation-rules/presets'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import { APSError } from '@/utils/domain/errors'
import { useFaciesStore } from '@/stores/facies'

const ruleStore = useTruncationRuleStore()
const rulePresetStore = useTruncationRulePresetStore()
const faciesStore = useFaciesStore()

const rule = computed(() => ruleStore.current)

const truncationRuleType = computed<Optional<TruncationRuleType>>(() => {
  return rulePresetStore.type
})

const truncationRuleComponent = computed<Optional<Component>>(() => {
  const mapping: Record<TruncationRuleType, Component> = {
    cubic: CubicSpecification,
    'non-cubic': NonCubicSpecification,
    bayfill: BayfillSpecification,
  }
  return truncationRuleType.value && rule.value
    ? mapping[truncationRuleType.value]
    : null
})

const useOverlay = computed({
  get: () => {
    return rule.value instanceof OverlayTruncationRule && rule.value.useOverlay
  },
  set: (value: boolean) => {
    if (!(rule.value instanceof OverlayTruncationRule)) {
      throw new APSError('useOverlay changes require OverlayTruncationRule')
    }
    ruleStore.toggleOverlay(rule.value, value)
  },
})

const notBayfill = computed(() => !(rule.value instanceof Bayfill))

const hasEnoughFacies = computed(() => {
  if (!rule.value) return true
  const numFacies = faciesStore.selected.length
  const numFaciesInBackground = new Set(
    (rule.value!).backgroundPolygons
      .map((polygon) => polygon.facies)
      .filter((facies) => !!facies),
  ).size
  return numFacies > numFaciesInBackground
})

const overlayErrors = computed<{ check: boolean; errorMessage: string }[]>(
  () => [
    {
      check: notBayfill.value,
      errorMessage: 'Bayfill cannot have user defined overlay facies',
    },
    {
      check: hasEnoughFacies.value,
      errorMessage: 'Too few facies has been selected for this truncation rule',
    },
  ],
)

const canUseOverlay = computed(
  () =>
    overlayErrors.value.every(({ check }) => check) || !!rule.value?.useOverlay,
)

const useOverlayTooltip = computed(
  () => overlayErrors.value.find(({ check }) => check)?.errorMessage,
)
</script>
