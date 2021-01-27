<template>
  <v-row
    no-gutters
  >
    <truncation-header />
    <div v-if="rule">
      <v-row
        no-gutters
      >
        <v-col
          v-if="notBayfill"
          cols="12"
        >
          <v-popover
            :disabled="canUseOverlay"
            trigger="hover"
          >
            <v-checkbox
              v-model="useOverlay"
              :disabled="!canUseOverlay"
              class="tooltip-target"
              label="Include Overlay Facies"
            />
            <span
              slot="popover"
            >
              {{ useOverlayTooltip }}
            </span>
          </v-popover>
        </v-col>
      </v-row>
      <v-row
        no-gutters
      >
        <v-col cols="12">
          <component
            :is="truncationRuleComponent"
            v-if="truncationRuleComponent && rule"
            :value="rule"
          />
        </v-col>
      </v-row>
      <v-row
        v-if="useOverlay"
        no-gutters
      >
        <v-col
          cols="12"
        >
          <overlay-facies
            :value="rule"
          />
        </v-col>
      </v-row>
    </div>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import BayfillSpecification from '@/components/specification/TruncationRule/Bayfill/index.vue'
import NonCubicSpecification from '@/components/specification/TruncationRule/NonCubic/index.vue'
import CubicSpecification from '@/components/specification/TruncationRule/Cubic/index.vue'
import TruncationHeader from '@/components/specification/TruncationRule/header.vue'
import OverlayFacies from '@/components/specification/TruncationRule/Overlay/index.vue'
import SectionTitle from '@/components/baseComponents/headings/SectionTitle.vue'

import { isUUID } from '@/utils/helpers'
import { Bayfill } from '@/utils/domain'
import Polygon from '@/utils/domain/polygon/base'
import TruncationRuleType from '@/utils/domain/truncationRule/base'
import { Optional } from '@/utils/typing'
import { Identified } from '@/utils/domain/bases/interfaces'
import { TruncationRuleTemplate } from '@/store/modules/truncationRules/typing'

@Component({
  components: {
    SectionTitle,
    TruncationHeader,
    OverlayFacies,
  },
})
export default class TruncationRule extends Vue {
  get truncationRuleType (): Optional<TruncationRuleTemplate> {
    const available: Identified<TruncationRuleTemplate> = this.$store.state.truncationRules.templates.types.available
    const type = this.$store.state.truncationRules.preset.type
    if (type && isUUID(type)) {
      return available[`${type}`]
    } else {
      return this.rule
        ? Object.values(available).find((item) => !!this.rule && item.type === this.rule.type) || null
        : null
    }
  }

  get truncationRuleComponent (): Optional<CubicSpecification | NonCubicSpecification | BayfillSpecification> {
    const mapping = {
      Cubic: CubicSpecification,
      'Non-Cubic': NonCubicSpecification,
      Bayfill: BayfillSpecification,
    }
    return this.truncationRuleType && this.rule
      ? mapping[this.truncationRuleType.name]
      : null
  }

  get rule (): Optional<TruncationRuleType> { return this.$store.getters.truncationRule }

  get useOverlay (): boolean { return this.rule ? this.rule.useOverlay : false }
  set useOverlay (val) { this.$store.dispatch('truncationRules/toggleOverlay', { rule: this.rule, value: val }) }

  get hasEnoughFacies (): boolean {
    if (!this.rule) return true
    const numFacies = Object.values(this.$store.getters['facies/selected']).length
    const numFaciesInBackground = [...new Set((this.rule.backgroundPolygons as Polygon[])
      .map(polygon => polygon.facies)
      .filter(name => !!name)
    )].length
    return numFacies > numFaciesInBackground
  }

  get notBayfill (): boolean { return !(this.rule instanceof Bayfill) }

  get overlayErrors (): { check: boolean, errorMessage: string }[] {
    return [
      { check: this.notBayfill, errorMessage: 'Bayfill cannot have user defined overlay facies' },
      { check: this.hasEnoughFacies, errorMessage: 'Too few facies has been selected for this truncation rule' },
    ]
  }

  get canUseOverlay (): boolean {
    return this.overlayErrors.every(({ check }) => check) || (!!this.rule && this.rule.useOverlay)
  }

  get useOverlayTooltip (): Optional<string> {
    for (const { check, errorMessage } of this.overlayErrors) {
      if (!check) return errorMessage
    }
    return null
  }
}
</script>
