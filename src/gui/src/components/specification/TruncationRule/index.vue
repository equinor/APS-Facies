<template>
  <v-expansion-panel
    :value="0"
  >
    <v-expansion-panel-content>
      <div slot="header">
        <h2>Truncation Rules</h2>
      </div>
      <truncation-header/>
      <v-layout
        v-if="rule"
        row
      >
        <v-flex xs12>
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
              slot="popover">{{ useOverlayTooltip }}</span>
          </v-popover>
        </v-flex>
      </v-layout>
      <v-flex xs12>
        <component
          :is="truncationRuleComponent"
          :value="rule"
        />
      </v-flex>
      <v-layout row>
        <v-flex
          v-if="useOverlay"
          xs12
        >
          <h5>Overlay Facies</h5>
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
import TruncationHeader from '@/components/specification/TruncationRule/header'
import OverlayFacies from '@/components/specification/TruncationRule/Overlay'
import { isUUID } from '@/utils/typing'

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
        'Cubic': null,
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
    hasEnoughFields () {
      const numFieldsAvailable = this.$store.getters.fields.length
      const numNecessaryFields = 1 + this.rule.backgroundFields.length + this.rule.overlayPolygons.length
      return numFieldsAvailable >= numNecessaryFields
    },
    hasEnoughFacies () {
      const numFacies = this.$store.getters.faciesTable
        .filter(facies => !!facies.selected)
        .length
      const numFaciesInBackground = [ ...new Set(Object.values(this.$store.getters.truncationRule.polygons)
        .map(polygon => polygon.facies)
        .filter(name => !!name)
      )].length
      return numFacies > numFaciesInBackground
    },
    canUseOverlay () {
      return this.hasEnoughFacies && this.hasEnoughFields
    },
    useOverlayTooltip () {
      return this.hasEnoughFacies
        ? this.hasEnoughFields
          ? null
          : 'There are not enough gaussian random fields to use with overlay'
        : 'There are not enough facies has been selected for this truncation rule'
    },
  },
}
</script>
