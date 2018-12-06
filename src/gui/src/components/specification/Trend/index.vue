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
          :grf-id="grfId"
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
            <v-select
              v-model="trendType"
              :items="availableTrends"
              label="Trend type"
            />
            <div
              v-if="hasLinearProperties"
            >
              <depositional-azimuth-angle
                :grf-id="grfId"
              />
              <stacking-angle-specification
                :grf-id="grfId"
              />
            </div>
            <migration-angle
              v-if="hasHyperbolicProperties"
              :grf-id="grfId"
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
                :grf-id="grfId"
              />
              <origin-specification
                :grf-id="grfId"
              />
            </div>
            <v-flex>
              <relative-size-of-ellipse
                v-if="hasEllipticConeProperties"
                :grf-id="grfId"
              />
            </v-flex>
          </v-flex>
        </v-layout>
      </v-container>
    </v-flex>
  </v-flex>
</template>

<script>
import { mapState } from 'vuex'
import { AppTypes } from '@/utils/typing'
import { notEmpty } from '@/utils'
import OriginSpecification from '@/components/specification/Trend/Origin'
import {
  StackingAngleSpecification,
  CurvatureSpecification,
  DepositionalAzimuthAngle,
  MigrationAngle,
  RelativeSizeOfEllipse,
  RelativeStandardDeviation,
} from '@/components/specification/Trend/InputFields'

export default {
  components: {
    StackingAngleSpecification,
    OriginSpecification,
    RelativeStandardDeviation,
    RelativeSizeOfEllipse,
    CurvatureSpecification,
    DepositionalAzimuthAngle,
    MigrationAngle,
  },

  props: {
    grfId: AppTypes.id.isRequired,
  },

  computed: {
    ...mapState({
      availableRmsTrendParameters: state => state.parameters.rmsTrend.available,
      availableTrends: state => state.constants.options.trends.available,
    }),
    trend () { return this.$store.state.gaussianRandomFields.fields[this.grfId].trend },
    hasLinearProperties () {
      return (
        notEmpty(this.trendType) &&
        this.notOneOf(['RMS_PARAM', 'NONE'])
      )
    },
    hasEllipticProperties () {
      return (
        this.hasLinearProperties &&
        this.notOneOf(['LINEAR'])
      )
    },
    hasHyperbolicProperties () {
      return (
        this.hasEllipticProperties &&
        this.notOneOf(['ELLIPTIC'])
      )
    },
    hasEllipticConeProperties () {
      return (
        this.hasHyperbolicProperties &&
        this.notOneOf(['HYPERBOLIC'])
      )
    },
    isRmsParameter () {
      return this.trend.type === 'RMS_PARAM'
    },
    trendType: {
      get: function () { return this.$store.state.gaussianRandomFields.fields[this.grfId].trend.type },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/trendType', { grfId: this.grfId, value }) }
    },
    trendParameter: {
      get: function () { return this.trend.parameter },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/trendParameter', { grfId: this.grfId, value }) }
    },
    useTrend: {
      get: function () { return this.trend.use },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/useTrend', { grfId: this.grfId, value }) },
    },
  },

  methods: {
    notOneOf (types) {
      return types.indexOf(this.trend.type) === -1
    },
    setTrend (event) {
      this.$store.dispatch('gaussianRandomFields/useTrend', event)
    },
    updateValue (prop, value) {
      if (prop === 'use') {
        this.trend.use = Boolean(value)
      } else {
        this.trend[`${prop}`] = value
      }
      this.$emit('input', this.trend)
    },
  }
}
</script>
