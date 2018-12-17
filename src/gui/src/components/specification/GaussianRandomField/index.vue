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
          expand
        />
      </v-flex>
      <v-flex xs1 />
      <v-flex xs5>
        <span>Variogram selection</span>
        <item-selection
          v-model="variogramType"
          :items="availableVariograms"
          :constraints="{ required: true }"
          label="Variogram"
        />
        <v-select
          v-model="alphaChannel"
          :items="alphaChannels"
          no-data-text="No truncation rule has been selected"
          label="Truncation Rule Role"
        >
          <template
            slot="item"
            slot-scope="{ item }"
          >
            ɑ<sub>{{ item }}</sub>
          </template>
          <template
            slot="selection"
            slot-scope="{ item }"
          >
            ɑ<sub>{{ item }}</sub>
          </template>
        </v-select>
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
        <span>Anisotropy direction</span>
        <anisotropy-direction
          :grf-id="grfId"
        />
        <power-specification
          v-if="isGeneralExponential"
          :grf-id="grfId"
        />
      </v-flex>
      <v-flex xs1 />
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
import { mapState, mapGetters } from 'vuex'
import cloneDeep from 'lodash/cloneDeep'

import rms from '@/api/rms'

import { hasValidChildren, invalidateChildren, notEmpty } from '@/utils'

import ItemSelection from '@/components/selection/dropdown/ItemSelection'
import GaussianPlot from '@/components/plot/GaussianPlot'
import TrendSpecification from '@/components/specification/Trend'
import RangeSpecification from '@/components/specification/GaussianRandomField/Range'
import AnisotropyDirection from '@/components/specification/GaussianRandomField/AnisotropyDirection'
import Power from '@/components/specification/GaussianRandomField/Power'
import VisualizationSettingsDialog from '@/components/specification/GaussianRandomField/VisualizationSettingsDialog'
import IconButton from '@/components/selection/IconButton'
import { AppTypes } from '@/utils/typing'

export default {
  name: 'GaussianRandomField',

  components: {
    ItemSelection,
    IconButton,
    PowerSpecification: Power,
    AnisotropyDirection,
    RangeSpecification,
    GaussianPlot,
    TrendSpecification,
    VisualizationSettingsDialog,
  },

  props: {
    value: AppTypes.gaussianRandomField.isRequired,
  },

  data () {
    return {
      waitingForSimulation: false,
    }
  },

  computed: {
    ...mapGetters({
      rule: 'truncationRule',
    }),
    ...mapState({
      availableVariograms: state => state.constants.options.variograms.available,
    }),
    gaussianFieldData () {
      return this.value
        ? this.value._data
        : []
    },
    alphaChannel: {
      get: function () {
        if (this.rule) {
          const item = this.rule.fields.find(item => item.field === this.grfId)
          return item ? item.channel : null
        } else {
          return null
        }
      },
      set: function (channel) { this.$store.dispatch('truncationRules/updateFields', { channel, selected: this.grfId }) }
    },
    alphaChannels () {
      return this.rule
        ? this.rule.fields.map(item => item.channel)
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
          settings: this.$store.getters.simulationSettings(this.grfId),
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
      const settings = cloneDeep(this.value.settings)
      this.$refs.visualisationSettings.open(settings, {})
        .then(({ save, settings }) => {
          if (save) {
            this.$store.dispatch('gaussianRandomFields/changeSettings', {
              grfId: this.grfId,
              settings
            }).then(() => this.updateSimulation())
          }
        })
    },
  }
}
</script>
