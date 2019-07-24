<template>
  <div>
    Origin
    <v-layout
      align-center
      justify-center
      row
      wrap
      fill-height
    >
      <v-flex
        md11
        lg3
      >
        <origin-x
          :value="value"
          :origin-type="originType"
          coordinate-axis="x"
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex
        md11
        lg3
      >
        <origin-y
          :value="value"
          :origin-type="originType"
          coordinate-axis="y"
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex
        v-if="!isEllipticCone"
        md11
        lg3
      >
        <origin-z
          :value="value"
          :origin-type="originType"
          coordinate-axis="z"
        />
      </v-flex>
    </v-layout>
    <v-select
      v-model="originType"
      :items="availableOriginTypes"
      label="Origin type"
    />
  </div>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { GaussianRandomField } from '@/utils/domain'
import OriginCoordinate from './Coordinate.vue'

@Component({
  components: {
    originX: OriginCoordinate,
    originY: OriginCoordinate,
    originZ: OriginCoordinate,
  },
})
export default class OriginSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get availableOriginTypes () { return this.$store.state.constants.options.origin.available }

  get trend () { return this.value.trend }

  get isEllipticCone () { return this.trend.type === 'ELLIPTIC_CONE' }

  get originType () { return this.trend.origin.type }
  set originType (value) { this.$store.dispatch('gaussianRandomFields/originType', { field: this.value, value }) }
}
</script>
