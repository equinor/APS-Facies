<template>
  <v-layout
    column
    justify-center
  >
    <v-layout
      justify-center
      align-end
    >
      <v-flex>
        <split-direction
          :value="value"
        />
      </v-flex>
      <v-flex>
        <numeric-field
          v-model="splitInto"
          :ranges="{ min: 2, max: Number.POSITIVE_INFINITY }"
          enforce-ranges
          label="Split into"
          discrete
        />
      </v-flex>
    </v-layout>
    <v-layout>
      <v-layout
        justify-center
      >
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
          Click in the table below to split/merge for Level 2 / Level 3.<br>
          When finished, add Facies with Proportion Fraction to the table.
        </help-icon>
      </v-layout>
    </v-layout>
    <v-layout
      justify-center
    >
      <cubic-topology-specification
        v-if="value.root"
        v-model="selected"
        :rule="value"
      />
    </v-layout>
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { DEFAULT_CUBIC_LEVELS } from '@/config'
import { getId } from '@/utils'

import HelpIcon from '@/components/baseComponents/HelpIcon.vue'
import TruncationMap from '@/components/plot/TruncationMap.vue'
import SplitDirection from '@/components/specification/TruncationRule/Cubic/table/specification/splitDirection.vue'
import CubicTopologySpecification from '@/components/specification/TruncationRule/Cubic/table/specification/specification.vue'
import NumericField from '@/components/selection/NumericField.vue'
import WaitButton from '@/components/baseComponents/WaitButton.vue'

import { Cubic, CubicPolygon } from '@/utils/domain'

@Component({
  components: {
    TruncationMap,
    HelpIcon,
    WaitButton,
    SplitDirection,
    CubicTopologySpecification,
    NumericField,
  }
})
export default class CubicTruncationRuleSpecification extends Vue {
  splitInto: number = 2
  selected: CubicPolygon[] = []

  @Prop({ required: true })
  readonly value!: Cubic

  split () {
    const polygon = (this.selected.length > 0)
      ? this.selected.pop()
      : this.value.root || new CubicPolygon({ order: -1 })
    this.$store.dispatch('truncationRules/split', { rule: this.value, polygon, value: this.splitInto })
  }
  merge () { this.$store.dispatch('truncationRules/merge', { rule: this.value, polygons: this.selected.splice(0, this.selected.length) }) }

  get canSplit (): boolean {
    return (
      this.selected.length === 1
      || this.value.backgroundPolygons.length === 0
    ) && this.canSplitDeeper
  }

  get canMerge (): boolean {
    return this.selected.length >= 2 && this.singleParentSelected
  }

  get canSplitDeeper (): boolean {
    return this.selected.length > 0
      ? this.selected.every(polygon => polygon.atLevel < this.maxLevel)
      : true
  }

  get splitError () {
    if (!this.canSplit) {
      if (!this.canSplitDeeper) return `A Cubic truncation rule may only be split into ${this.maxLevel} levels`
      if (this.selected.length > 1) return 'Only a single polygon may be split at the time'
      if (this.selected.length === 0) return 'Click on the polygon that should be split'
    }
    return ''
  }

  get mergeError () {
    if (!this.canMerge) {
      if (!this.singleParentSelected) return 'Only polygons having the same parent may be merged'
    }
    return ''
  }

  get maxLevel () { return DEFAULT_CUBIC_LEVELS }

  get singleParentSelected (): boolean {
    const parents = this.selected.reduce((parents, polygon) => {
      parents.add(getId(polygon.parent))
      return parents
    }, new Set())
    return parents.size === 1
  }
}
</script>
