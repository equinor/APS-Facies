<template>
  <v-flex>
    Trend
    <v-layout
      row
    >
      <v-flex xs6>
        <v-checkbox
          v-model="useTrend"
          label="Apply trend to field"
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex xs5>
        <relative-standard-deviation
          v-if="useTrend"
          :value="value"
        />
      </v-flex>
    </v-layout>
    <v-flex
      v-if="useTrend"
    >
      <v-container>
        <v-layout
          align-center
          justify-center
          row
          fill-height
        >
          <v-flex xs6>
            <item-selection
              v-model="trendType"
              :items="availableTrends"
              :constraints="{ required: true }"
              label="Trend type"
            />
            <div
              v-if="hasLinearProperties"
            >
              <depositional-azimuth-angle
                :value="value"
              />
              <stacking-angle-specification
                :value="value"
              />
            </div>
            <migration-angle
              v-if="hasHyperbolicProperties"
              :value="value"
            />
          </v-flex>
          <v-flex xs1 />
          <v-flex xs5>
            <v-select
              v-if="isRmsParameter"
              v-model="trendParameter"
              :items="availableRmsTrendParameters"
              label="Trend parameter"
            />
            <div
              v-if="hasEllipticProperties"
            >
              <curvature-specification
                :value="value"
              />
              <origin-specification
                :value="value"
              />
            </div>
            <v-flex>
              <relative-size-of-ellipse
                v-if="hasEllipticConeProperties"
                :value="value"
              />
            </v-flex>
          </v-flex>
        </v-layout>
      </v-container>
    </v-flex>
  </v-flex>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import { TrendType } from '@/utils/domain/gaussianRandomField/trend'

import { notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection.vue'
import OriginSpecification from '@/components/specification/Trend/Origin/index.vue'
import {
  StackingAngleSpecification,
  CurvatureSpecification,
  DepositionalAzimuthAngle,
  MigrationAngle,
  RelativeSizeOfEllipse,
  RelativeStandardDeviation,
} from '@/components/specification/Trend/InputFields'

@Component({
  components: {
    ItemSelection,
    StackingAngleSpecification,
    OriginSpecification,
    RelativeStandardDeviation,
    RelativeSizeOfEllipse,
    CurvatureSpecification,
    DepositionalAzimuthAngle,
    MigrationAngle,
  },
})
export default class TrendSpecification extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField

  get availableRmsTrendParameters () { return this.$store.state.parameters.rmsTrend.available }
  get availableTrends () { return this.$store.state.constants.options.trends.available }

  get trend () { return this.value.trend }

  get hasLinearProperties () {
    return (
      notEmpty(this.trendType)
      && this.notOneOf(['RMS_PARAM', 'NONE'])
    )
  }
  get hasEllipticProperties () {
    return (
      this.hasLinearProperties
      && this.notOneOf(['LINEAR'])
    )
  }
  get hasHyperbolicProperties () {
    return (
      this.hasEllipticProperties
      && this.notOneOf(['ELLIPTIC'])
    )
  }
  get hasEllipticConeProperties () {
    return (
      this.hasHyperbolicProperties
      && this.notOneOf(['HYPERBOLIC'])
    )
  }
  get isRmsParameter () { return this.trend.type === 'RMS_PARAM' }

  get trendType () { return this.value.trend.type }
  set trendType (value) { this.$store.dispatch('gaussianRandomFields/trendType', { field: this.value, value }) }

  get trendParameter () { return this.trend.parameter }
  set trendParameter (value) { this.$store.dispatch('gaussianRandomFields/trendParameter', { field: this.value, value }) }

  get useTrend () { return this.trend.use }
  set useTrend (value) { this.$store.dispatch('gaussianRandomFields/useTrend', { field: this.value, value }) }

  notOneOf (types: TrendType[]): boolean {
    return types.indexOf(this.trend.type) === -1
  }
}
</script>
