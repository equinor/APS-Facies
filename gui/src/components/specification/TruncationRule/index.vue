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
        <overlay-facies :value="rule" />
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

import { isUUID } from '@/utils/helpers'
import { Bayfill } from '@/utils/domain'
import Polygon from '@/utils/domain/polygon/base'
import { Optional } from '@/utils/typing'
import { TruncationRuleTemplate } from '@/store/modules/truncationRules/typing'
import { useStore } from '../../../store'
import { RootGetters } from '../../../store/typing'
import { computed } from 'vue'
import { type Component } from 'vue'

const store = useStore()

const rule = computed(() => (store.getters as RootGetters).truncationRule)

const truncationRuleType = computed<Optional<TruncationRuleTemplate>>(() => {
  const available = store.state.truncationRules.templates.types.available
  const type = store.state.truncationRules.preset.type
  if (type && isUUID(type)) {
    return available[type]
  } else {
    return (
      Object.values(available).find(
        (item) => item.type === rule?.value?.type,
      ) ?? null
    )
  }
})

const truncationRuleComponent = computed<Optional<Component>>(() => {
  const mapping = {
    Cubic: CubicSpecification,
    'Non-Cubic': NonCubicSpecification,
    Bayfill: BayfillSpecification,
  }
  return truncationRuleType.value && rule.value
    ? mapping[truncationRuleType.value.name]
    : null
})

const useOverlay = computed({
  get: () => rule.value?.useOverlay ?? false,
  set: (value: boolean) =>
    store.dispatch('truncationRules/toggleOverlay', {
      rule: rule.value,
      value: value,
    }),
})

const notBayfill = computed(() => !(rule.value instanceof Bayfill))

const hasEnoughFacies = computed(() => {
  if (!rule.value) return true
  const numFacies = Object.values(
    (store.getters as RootGetters)['facies/selected'],
  ).length
  const numFaciesInBackground = [
    ...new Set(
      (rule.value.backgroundPolygons as Polygon[])
        .map((polygon) => polygon.facies)
        .filter((name) => !!name),
    ),
  ].length
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
    overlayErrors.value.every(({ check }) => check) || rule.value?.useOverlay,
)

const useOverlayTooltip = computed(
  () => overlayErrors.value.find(({ check }) => check)?.errorMessage,
)
</script>
