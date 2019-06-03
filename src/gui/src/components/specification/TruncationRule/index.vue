<template>
  <v-expansion-panel
    :value="0"
  >
    <v-expansion-panel-content>
      <div slot="header">
        <h2>Truncation Rules</h2>
      </div>
      <truncation-header />
      <v-layout
        v-if="rule"
        row
      >
        <v-flex
          v-if="notBayfill"
          xs12
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
        </v-flex>
      </v-layout>
      <v-flex xs12>
        <component
          :is="truncationRuleComponent"
          v-if="truncationRuleComponent"
          :value="rule"
        />
      </v-flex>
      <v-layout row>
        <v-flex
          v-if="useOverlay"
          xs12
        >
          <overlay-facies
            :value="rule"
          />
        </v-flex>
      </v-layout>
    </v-expansion-panel-content>
  </v-expansion-panel>
</template>

<script>
import BayfillSpecification from '@/components/specification/TruncationRule/Bayfill'
import NonCubicSpecification from '@/components/specification/TruncationRule/NonCubic'
import CubicSpecification from '@/components/specification/TruncationRule/Cubic'
import TruncationHeader from '@/components/specification/TruncationRule/header'
import OverlayFacies from '@/components/specification/TruncationRule/Overlay'
import { isUUID } from '@/utils/helpers'
import { Bayfill } from '@/utils/domain'

export default {
  components: {
    TruncationHeader,
    OverlayFacies,
  },

  computed: {
    truncationRuleType () {
      const available = this.$store.state.truncationRules.templates.types.available
      let type = this.$store.state.truncationRules.preset.type
      if (type && isUUID(type)) {
        return available[`${type}`]
      } else {
        return this.rule
          ? Object.values(available).find(item => item.type === this.rule.type) || null
          : null
      }
    },
    truncationRuleComponent () {
      const mapping = {
        'Cubic': CubicSpecification,
        'Non-Cubic': NonCubicSpecification,
        'Bayfill': BayfillSpecification,
      }
      return this.truncationRuleType && this.rule
        ? mapping[this.truncationRuleType.name]
        : null
    },
    rule () {
      return this.$store.getters.truncationRule
    },
    useOverlay: {
      get: function () { return this.rule ? this.rule.useOverlay : false },
      set: function (val) { this.$store.dispatch('truncationRules/toggleOverlay', { rule: this.rule, value: val }) },
    },
    hasEnoughFacies () {
      const numFacies = Object.values(this.$store.state.facies.available).length
      const numFaciesInBackground = [ ...new Set(this.rule.backgroundPolygons
        .map(polygon => polygon.facies)
        .filter(name => !!name)
      )].length
      return numFacies > numFaciesInBackground
    },
    notBayfill () {
      return !(this.rule instanceof Bayfill)
    },
    overlayErrors () {
      return [
        { check: this.notBayfill, errorMessage: 'Bayfill cannot have user defined overlay facies' },
        { check: this.hasEnoughFacies, errorMessage: 'Too few facies has been selected for this truncation rule' },
      ]
    },
    canUseOverlay () {
      return this.overlayErrors.every(({ check }) => !!check) || this.rule.useOverlay
    },
    useOverlayTooltip () {
      for (const { check, errorMessage } of this.overlayErrors) {
        if (!check) return errorMessage
      }
      return null
    },
  },
}
</script>
