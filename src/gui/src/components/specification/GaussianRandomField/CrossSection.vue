<template>
  <v-row
    class="ma-2"
  >
    <!--Cross section-->
    <v-col>
      <v-select
        v-model="type"
        :items="['IJ', 'IK', 'JK']"
        label="Cross section type"
        required
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import { Store } from '@/store/typing'

import FractionField from '@/components/selection/FractionField.vue'

@Component({
  components: {
    FractionField,
  },
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
