<template>
  <div>
    Origin
    <v-row
      class="fill-height"
      align="center"
      justify="center"
    >
      <v-col
        :class="coordinateClass"
      >
        <origin-x
          :value="value"
          :origin-type="originType"
          coordinate-axis="x"
          @update:error="e => update('x', e)"
        />
      </v-col>
      <v-col
        :class="coordinateClass"
      >
        <origin-y
          :value="value"
          :origin-type="originType"
          coordinate-axis="y"
          @update:error="e => update('y', e)"
        />
      </v-col>
      <v-col
        v-if="!isEllipticCone"
        :class="coordinateClass"
      >
        <origin-z
          :value="value"
          :origin-type="originType"
          coordinate-axis="z"
          @update:error="e => update('z', e)"
        />
      </v-col>
    </v-row>
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
import Trend, { OriginType } from '@/utils/domain/gaussianRandomField/trend'
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

  get availableOriginTypes (): string[] { return this.$store.state.constants.options.origin.available }

  get trend (): Trend { return this.value.trend }

  get isEllipticCone (): boolean { return this.trend.type === 'ELLIPTIC_CONE' }

  get originType (): OriginType { return this.trend.origin.type }
  set originType (value) { this.$store.dispatch('gaussianRandomFields/originType', { field: this.value, value }) }

  get coordinateClass (): string {
    return 'pa-1 pt-2'
  }

  @Watch('invalid', { deep: true })
  propagateError ({ x, y, z }: Invalid): void {
    this.$emit('update:error', x || y || (!this.isEllipticCone && z))
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }
}
</script>
