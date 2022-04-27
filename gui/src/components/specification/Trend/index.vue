<template>
  <v-col cols="12">
    <h4>Trend</h4>
    <v-row>
      <v-col cols="6">
        <v-checkbox
          v-model="useTrend"
          label="Apply trend to field"
        />
      </v-col>
      <v-spacer />
      <v-col cols="6">
        <relative-standard-deviation
          v-if="useTrend"
          :value="value"
          @update:error="e => update('relativeStdDev', e)"
        />
      </v-col>
    </v-row>
    <v-col
      v-if="useTrend"
    >
      <v-row
        class="fill-height"
        align="center"
        justify="center"
        no-gutters
      >
        <v-col cols="6">
          <item-selection
            v-model="trendType"
            :items="availableTrends"
            :constraints="{ required: true }"
            label="Trend type"
            @update:error="e => update('type', e)"
          />
          <div
            v-if="hasLinearProperties"
          >
            <depositional-azimuth-angle
              :value="value"
              @update:error="e => update('azimuth', e)"
            />
            <stacking-angle-specification
              :value="value"
              @update:error="e => update('stacking', e)"
            />
          </div>
          <migration-angle
            v-if="hasHyperbolicProperties"
            :value="value"
            @update:error="e => update('migration', e)"
          />
        </v-col>
        <v-spacer />
        <v-col cols="5">
          <v-select
            v-if="isRmsParameter"
            v-model="trendParameter"
            :items="availableRmsTrendParameters"
            label="Trend parameter"
          />
          <v-select
            v-if="isRmsTrendMap"
            v-model="trendMapZone"
            v-tooltip="'Select zone name from Zones folder for maps'"
            :items="availableRmsTrendZones"
            label="Zone name"
          />
          <v-select
            v-if="isRmsTrendMap"
            v-model="trendMapName"
            v-tooltip="'Select surface with 2D trend corresponding to selected zone'"
            :items="availableRmsTrendMaps"
            :disabled="!hasDefinedRmsTrendZone"
            label="Trend map"
          />
          <div
            v-if="hasEllipticProperties"
          >
            <curvature-specification
              :value="value"
              @update:error="e => update('curvature', e)"
            />
            <origin-specification
              :value="value"
              @update:error="e => update('origin', e)"
            />
          </div>
          <v-col>
            <relative-size-of-ellipse
              v-if="hasEllipticConeProperties"
              :value="value"
              @update:error="e => update('relativeEllipseSize', e)"
            />
          </v-col>
        </v-col>
      </v-row>
    </v-col>
  </v-col>
</template>

<script lang="ts">
import { Component, Prop, Vue, Watch } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import Trend, { TrendType } from '@/utils/domain/gaussianRandomField/trend'
import { Store } from '@/store/typing'
import { ListItem } from '@/utils/typing'

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

import { TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION } from '@/config'
import type { TrendMap } from '@/store/modules/parameters/rmsTrendMapZones'

interface Invalid {
  relativeStdDev: boolean
  type: boolean
  azimuth: boolean
  stacking: boolean
  migration: boolean
  curvature: boolean
  origin: boolean
  relativeEllipseSize: boolean
}

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

  invalid: Invalid = {
    relativeStdDev: false,
    type: false,
    azimuth: false,
    stacking: false,
    migration: false,
    curvature: false,
    origin: false,
    relativeEllipseSize: false,
  }

  get availableRmsTrendParameters (): string[] { return this.$store.state.parameters.rmsTrend.available }
  private get rmsTrendMapZones (): TrendMap[] { return this.$store.state.parameters.rmsTrendMapZones.available }
  get availableRmsTrendZones (): string[] {
    return this.rmsTrendMapZones
      .filter(zone => zone.representations.length > 0)
      .map(({ name }) => name)
  }

  private get trendMapZoneLookup (): Record<string, string[]> {
    return this.rmsTrendMapZones
      .reduce((mapping, trendMap) => {
        mapping[trendMap.name] = trendMap.representations
        return mapping
      }, ({}))
  }

  get availableRmsTrendMaps (): string[] {
    if (!this.trendMapZone) return []
    return this.trendMapZoneLookup[this.trendMapZone]
  }

  get availableTrends (): ListItem<string>[] {
    return (this.$store as Store).state.constants.options.trends.available
      .map(name => {
        return {
          text: name,
        }
      })
  }

  get trend (): Trend { return this.value.trend }

  get hasLinearProperties (): boolean {
    return (
      notEmpty(this.trendType)
      && this.notOneOf(TREND_NOT_IMPLEMENTED_PREVIEW_VISUALIZATION)
    )
  }

  get hasEllipticProperties (): boolean {
    return (
      this.hasLinearProperties
      && this.notOneOf(['LINEAR'])
    )
  }

  get hasHyperbolicProperties (): boolean {
    return (
      this.hasEllipticProperties
      && this.notOneOf(['ELLIPTIC'])
    )
  }

  get hasEllipticConeProperties (): boolean {
    return (
      this.hasHyperbolicProperties
      && this.notOneOf(['HYPERBOLIC'])
    )
  }

  get isRmsParameter (): boolean { return this.trend.type === 'RMS_PARAM' }
  get isRmsTrendMap (): boolean { return this.trend.type === 'RMS_TRENDMAP' }

  get trendType (): TrendType { return this.value.trend.type }
  set trendType (value) { this.$store.dispatch('gaussianRandomFields/trendType', { field: this.value, value }) }

  get trendParameter (): string | null { return this.trend.parameter }
  set trendParameter (value) { this.$store.dispatch('gaussianRandomFields/trendParameter', { field: this.value, value }) }

  get trendMapName (): string | null { return this.trend.trendMapName }
  set trendMapName (value) { this.$store.dispatch('gaussianRandomFields/trendMapName', { field: this.value, value }) }

  get trendMapZone (): string | null { return this.trend.trendMapZone }
  set trendMapZone (value) { this.$store.dispatch('gaussianRandomFields/trendMapZone', { field: this.value, value }) }

  get useTrend (): boolean { return this.trend.use }
  set useTrend (value) { this.$store.dispatch('gaussianRandomFields/useTrend', { field: this.value, value }) }

  get hasDefinedRmsTrendZone (): boolean { return (this.trendMapZone != null) }

  notOneOf (types: TrendType[]): boolean {
    return types.indexOf(this.trend.type) === -1
  }

  @Watch('invalid', { deep: true })
  onInvalidChanged (value: Invalid): void {
    const invalid = Object.values(value).some(invalid => invalid)
    this.$emit('update:error', this.useTrend && invalid)
  }

  update (type: string, value: boolean): void {
    Vue.set(this.invalid, type, value)
  }
}
</script>
