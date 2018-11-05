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
        <v-btn
          :disabled="!canSimulate"
          @click="updateSimulation"
        >
          <span v-if="!waitingForSimulation">Refresh</span>
          <span v-else><v-progress-circular indeterminate/></span>
        </v-btn>
        <v-btn
          @click="openVisualizationSettings"
        >
          Settings
        </v-btn>
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

export default {
  name: 'GaussianRandomField',

  components: {
    PowerSpecification: Power,
    AnisotropyDirection,
    RangeSpecification,
    GaussianPlot,
    TrendSpecification,
    VisualizationSettingsDialog,
  },

  props: {
    grfId: VueTypes.string.isRequired,
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
      return this.field
        ? this.field._data
        : []
    },
    isGeneralExponential () { return this.variogramType === 'GENERAL_EXPONENTIAL' },
    field () { return this.$store.state.gaussianRandomFields.fields[this.grfId] },
    variogram () { return this.field.variogram },
    trend () { return this.field.trend },
    fieldName () { return this.field.name },
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
    reseedOnRefresh () { return this.field.settings.seed.autoRenew }
  },

  methods: {
    async simulation () {
      if (this.reseedOnRefresh) {
        await this.$store.dispatch('gaussianRandomFields/newSeed', { grfId: this.grfId })
      }
      return this.$store.dispatch('gaussianRandomFields/updateSimulationData', {
        grfId: this.grfId,
        data: await rms.simulateGaussianField({
          name: this.field.name,
          variogram: this.variogram,
          trend: this.trend,
          settings: this.field.settings,
        })
      })
    },
    updateSimulation () {
      this.waitingForSimulation = true
      this.simulation()
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
          type: this.field.settings.crossSection.type,
          relativePosition: this.field.settings.crossSection.relativePosition,
        },
        gridAzimuth: this.field.settings.gridAzimuth,
        gridSize: {
          x: this.field.settings.gridSize.x,
          y: this.field.settings.gridSize.y,
          z: this.field.settings.gridSize.z,
        },
        simulationBox: {
          x: this.field.settings.simulationBox.x,
          y: this.field.settings.simulationBox.y,
          z: this.field.settings.simulationBox.z,
        },
        seed: {
          value: this.field.settings.seed.value,
          autoRenew: this.field.settings.seed.autoRenew
        },
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
