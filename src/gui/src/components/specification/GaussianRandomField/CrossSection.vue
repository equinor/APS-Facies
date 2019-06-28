<template>
  <v-layout
    ma-2
    wrap
  >
    <!--Cross section-->
    <v-flex
      xs12
      sm6
      md6
    >
      <v-select
        v-model="type"
        :items="['IJ', 'IK', 'JK']"
        label="Cross section type"
        required
      />
    </v-flex>
    <v-flex
      xs12
      sm6
      md6
    >
      <fraction-field
        v-model="relativePosition"
        label="Relative position"
        required
      />
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'
import { debounce } from 'lodash'

import { Store } from '@/store/typing'

import FractionField from '@/components/selection/FractionField.vue'

@Component({
  components: {
    FractionField,
  },

  computed: {
    relativePosition: {
      get (this: CrossSection) {
        return this.crossSection
          ? this.crossSection.relativePosition
          : 0.5
      },
      set: debounce(function (this: CrossSection, value) {
        if (!this.crossSection) return
        this.$store.dispatch('gaussianRandomFields/crossSections/changeRelativePosition', {
          id: this.crossSection.id,
          relativePosition: value
        })
      }, 500)
    }
  }
})
export default class CrossSection extends Vue {
  get crossSection () { return (this.$store as Store).getters['gaussianRandomFields/crossSections/current'] }

  public get type (): string { return this.crossSection ? this.crossSection.type : 'IJ' }
  public set type (value: string) {
    if (!this.crossSection) return
    this.$store.dispatch('gaussianRandomFields/crossSections/changeType', { id: this.crossSection.id, type: value })
  }
}
</script>
