<template>
  <v-container class="column">
    <v-row justify="center" align="end">
      <v-col cols="6">
        <split-direction :value="value" />
      </v-col>
      <v-col cols="6">
        <numeric-field
          v-model="splitInto"
          :ranges="{ min: 2, max: Number.POSITIVE_INFINITY }"
          enforce-ranges
          label="Split into"
          discrete
        />
      </v-col>
    </v-row>
    <v-row class="ma-1">
      <v-row justify="center" align="center">
        <wait-button
          title="Split"
          outlined
          :disabled="!canSplit"
          :tooltip-text="splitError"
          @click="split"
        />
        <wait-button
          title="Merge"
          outlined
          :disabled="!canMerge"
          :tooltip-text="mergeError"
          @click="merge"
        />
        <help-icon>
          Click in the table below to split/merge for Level 2 / Level 3.<br />
          When finished, add Facies with Proportion Fraction to the table.
        </help-icon>
      </v-row>
    </v-row>
    <v-row justify="center" no-gutters>
      <cubic-topology-specification
        v-if="value.backgroundPolygons.length > 0"
        v-model="selected"
        :rule="value"
      />
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { DEFAULT_CUBIC_LEVELS } from '@/config'
import { getId } from '@/utils'

import HelpIcon from '@/components/baseComponents/HelpIcon.vue'
import SplitDirection from '@/components/specification/TruncationRule/Cubic/table/specification/splitDirection.vue'
import CubicTopologySpecification from '@/components/specification/TruncationRule/Cubic/table/specification/specification.vue'
import NumericField from '@/components/selection/NumericField.vue'
import WaitButton from '@/components/baseComponents/WaitButton.vue'

import { Cubic, CubicPolygon } from '@/utils/domain'
import { ref, computed } from 'vue'
import { useStore } from '../../../../../../store'

const props = defineProps<{ value: Cubic }>()
const store = useStore()

const splitInto = ref(2)
const selected = ref<CubicPolygon[]>([])

function split() {
  const polygon =
    selected.value.length > 0 ? selected.value.pop() : props.value.root
  if (!polygon) {
    throw new Error('The truncation rule has no root')
  }
  store.dispatch('truncationRules/split', {
    rule: props.value,
    polygon,
    value: splitInto.value,
  })
}

function merge() {
  store.dispatch('truncationRules/merge', {
    rule: props.value,
    polygons: selected.value.splice(0, selected.value.length),
  })
}

const canSplit = computed(
  () =>
    (selected.value.length === 1 ||
      props.value.backgroundPolygons.length === 0) &&
    canSplitDeeper.value,
)

const canMerge = computed(
  () => selected.value.length >= 2 && singleParentSelected.value,
)
const maxLevel = DEFAULT_CUBIC_LEVELS
const canSplitDeeper = computed(() =>
  selected.value.length > 0
    ? selected.value.every((polygon) => polygon.atLevel < maxLevel)
    : true,
)

const splitError = computed(() => {
  if (canSplit.value) return ''
  if (!canSplitDeeper.value)
    return `A Cubic truncation rule may only be split into ${maxLevel} levels`
  if (selected.value.length > 1)
    return 'Only a single polygon may be split at the time'
  if (selected.value.length === 0)
    return 'Click on the polygon that should be split'
  return undefined
})

const mergeError = computed(() => {
  if (canMerge.value) return ''

  const length = selected.value.length
  if (length === 0) return 'No polygons are selected for merging'
  if (length === 1) return 'A single polygon cannot be merged into itself'
  if (!singleParentSelected.value)
    return 'Only polygons having the same parent may be merged'
  return 'Unable to merge'
})

const singleParentSelected = computed(() => {
  const parents = selected.value.reduce(
    (parents, polygon) => parents.add(getId(polygon.parent)),
    new Set(),
  )
  return parents.size === 1
})
</script>
