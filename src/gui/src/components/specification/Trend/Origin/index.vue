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
          @update:error="e => update('x', e)"
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
          @update:error="e => update('y', e)"
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
          @update:error="e => update('z', e)"
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
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'
import { GaussianRandomField } from '@/utils/domain'
import OriginCoordinate from './Coordinate.vue'

interface Invalid {
  x: boolean
  y: boolean
  z: boolean
}

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

  invalid: Invalid = {
    x: false,
    y: false,
    z: false,
  }

  get availableOriginTypes () { return this.$store.state.constants.options.origin.available }

  get trend () { return this.value.trend }

  get isEllipticCone () { return this.trend.type === 'ELLIPTIC_CONE' }

  get originType () { return this.trend.origin.type }
  set originType (value) { this.$store.dispatch('gaussianRandomFields/originType', { field: this.value, value }) }

  @Watch('invalid', { deep: true })
  propagateError ({ x, y, z }: Invalid) {
    this.$emit('update:error', x || y || (!this.isEllipticCone && z))
  }

  update (type: string, value: boolean) {
    Vue.set(this.invalid, type, value)
  }
}
</script>
