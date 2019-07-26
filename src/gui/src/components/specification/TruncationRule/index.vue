<template>
  <div>
    <truncation-header />
    <v-layout
      v-if="rule"
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
        v-if="truncationRuleComponent && rule"
        :value="rule"
      />
    </v-flex>
    <v-layout>
      <v-flex
        v-if="useOverlay"
        xs12
      >
        <overlay-facies
          :value="rule"
        />
      </v-flex>
    </v-layout>
  </div>
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
import { Bayfill, Facies } from '@/utils/domain'

@Component({
  components: {
    SectionTitle,
    TruncationHeader,
    OverlayFacies,
  },
})
export default class TruncationRule extends Vue {
  get truncationRuleType () {
    const available = this.$store.state.truncationRules.templates.types.available
    const type = this.$store.state.truncationRules.preset.type
    if (type && isUUID(type)) {
      return available[`${type}`]
    } else {
      return this.rule
        // @ts-ignore
        ? Object.values(available).find(item => item.type === this.rule.type) || null
        : null
    }
  }

  get truncationRuleComponent () {
    const mapping = {
      'Cubic': CubicSpecification,
      'Non-Cubic': NonCubicSpecification,
      'Bayfill': BayfillSpecification,
    }
    return this.truncationRuleType && this.rule
      ? mapping[this.truncationRuleType.name]
      : null
  }

  get rule () { return this.$store.getters.truncationRule }

  get useOverlay () { return this.rule ? this.rule.useOverlay : false }
  set useOverlay (val) { this.$store.dispatch('truncationRules/toggleOverlay', { rule: this.rule, value: val }) }

  get hasEnoughFacies () {
    const numFacies = Object.values(this.$store.getters['facies/selected']).length
    const numFaciesInBackground = [ ...new Set((this.rule.backgroundPolygons as Facies[])
      .map(polygon => polygon.facies)
      .filter(name => !!name)
    )].length
    return numFacies > numFaciesInBackground
  }

  get notBayfill () { return !(this.rule instanceof Bayfill) }

  get overlayErrors () {
    return [
      { check: this.notBayfill, errorMessage: 'Bayfill cannot have user defined overlay facies' },
      { check: this.hasEnoughFacies, errorMessage: 'Too few facies has been selected for this truncation rule' },
    ]
  }

  get canUseOverlay () {
    return this.overlayErrors.every(({ check }) => check) || this.rule.useOverlay
  }

  get useOverlayTooltip () {
    for (const { check, errorMessage } of this.overlayErrors) {
      if (!check) return errorMessage
    }
    return null
  }
}
</script>
