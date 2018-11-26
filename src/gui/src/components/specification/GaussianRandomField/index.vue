<template>
  <v-container>
    <v-layout
      child-flex
      row
      wrap
    >
      <v-flex xs6>
        <gaussian-plot
          :data="gaussianFieldData"
        />
      </v-flex>
      <v-flex xs1/>
      <v-flex
        xs5
      >
        Variogram selection
        <v-select
          :items="availableVariograms"
          v-model="variogramType"
          label="Variogram"
        />
        <v-select
          :items="[]"
          label="Truncation Rule Role"
        />
        <icon-button
          :disabled="!canSimulate"
          icon="random"
          @click="() => updateSimulation(true)"
        />
        <icon-button
          :disabled="!canSimulate"
          :waiting="waitingForSimulation"
          icon="refresh"
          @click="() => updateSimulation(false)"
        />
        <icon-button
          icon="settings"
          @click="openVisualizationSettings"
        />
        <visualization-settings-dialog
          ref="visualisationSettings"
        />
      </v-flex>
      <!--New line-->
      <v-flex xs6>
        Anisotropy direction
        <anisotropy-direction
          :grf-id="grfId"
        />
        <power-specification
          v-if="isGeneralExponential"
          :grf-id="grfId"
        />
      </v-flex>
      <v-flex xs1/>
      <v-flex xs5>
        Ranges
        <range-specification
          :grf-id="grfId"
        />
      </v-flex>
      <!--New line-->
      <trend-specification
        :grf-id="grfId"
      />
    </v-layout>
  </v-container>
</template>

<script>
import { mapState } from 'vuex'
import VueTypes from 'vue-types'

import rms from '@/api/rms'

import { hasValidChildren, invalidateChildren, notEmpty } from '@/utils'

import GaussianPlot from '@/components/plot/GaussianPlot'
import TrendSpecification from '@/components/specification/Trend'
import RangeSpecification from '@/components/specification/GaussianRandomField/Range'
import AnisotropyDirection from '@/components/specification/GaussianRandomField/AnisotropyDirection'
import Power from '@/components/specification/GaussianRandomField/Power'
import VisualizationSettingsDialog from '@/components/specification/GaussianRandomField/VisualizationSettingsDialog'
import IconButton from '@/components/selection/IconButton'
import { GaussianRandomField } from '@/store/utils/domain'

export default {
  name: 'GaussianRandomField',

  components: {
    IconButton,
    PowerSpecification: Power,
    AnisotropyDirection,
    RangeSpecification,
    GaussianPlot,
    TrendSpecification,
    VisualizationSettingsDialog,
  },

  props: {
    value: VueTypes.instanceOf(GaussianRandomField).isRequired,
  },

  data () {
    return {
      waitingForSimulation: false,
    }
  },

  computed: {
    ...mapState({
      availableVariograms: state => state.constants.options.variograms.available,
    }),
    gaussianFieldData () {
      return this.value
        ? this.value._data
        : []
    },
    isGeneralExponential () { return this.variogramType === 'GENERAL_EXPONENTIAL' },
    grfId () { return this.value.id },
    variogram () { return this.value.variogram },
    trend () { return this.value.trend },
    fieldName () { return this.value.name },
    canSimulate: {
      cache: false,
      get: function () {
        return (
          notEmpty(this.variogramType) &&
          this.isValid &&
          !this.waitingForSimulation
        )
      },
    },
    isValid: {
      cache: false,
      get: function () { return hasValidChildren(this) }
    },
    variogramType: {
      get: function () { return this.variogram.type },
      set: function (value) { this.$store.dispatch('gaussianRandomFields/variogramType', { grfId: this.grfId, value }) }
    },
  },

  beforeMount () {
    this.updateSimulation()
  },

  methods: {
    async simulation (renew = false) {
      if (renew) {
        await this.$store.dispatch('gaussianRandomFields/newSeed', { grfId: this.grfId })
      }
      return this.$store.dispatch('gaussianRandomFields/updateSimulationData', {
        grfId: this.grfId,
        data: await rms.simulateGaussianField({
          name: this.value.name,
          variogram: this.variogram,
          trend: this.trend,
          settings: this.value.settings,
        })
      })
    },
    updateSimulation (renew = false) {
      this.waitingForSimulation = true
      this.simulation(renew)
        .then(() => {
          this.waitingForSimulation = false
        })
        .catch(reason => {
          this.waitingForSimulation = false
          invalidateChildren(this)
        })
    },
    openVisualizationSettings () {
      const settings = {
        crossSection: {
          type: this.value.settings.crossSection.type,
          relativePosition: this.value.settings.crossSection.relativePosition,
        },
        gridAzimuth: this.value.settings.gridAzimuth,
        gridSize: {
          x: this.value.settings.gridSize.x,
          y: this.value.settings.gridSize.y,
          z: this.value.settings.gridSize.z,
        },
        simulationBox: {
          x: this.value.settings.simulationBox.x,
          y: this.value.settings.simulationBox.y,
          z: this.value.settings.simulationBox.z,
        },
        seed: this.value.settings.seed,
      }
      this.$refs.visualisationSettings.open(settings, {})
        .then(({ save, settings }) => {
          if (save) {
            this.$store.dispatch('gaussianRandomFields/changeSettings', {
              grfId: this.grfId,
              settings
            })
          }
        })
    },
  }
}
</script>
