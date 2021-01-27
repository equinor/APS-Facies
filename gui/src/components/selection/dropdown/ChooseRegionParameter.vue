<template>
  <v-row
    justify="space-between"
    no-gutters
  >
    <v-col cols="0">
      <warning-dialog
        ref="warning"
        html
      />
    </v-col>
    <v-col cols="3">
      <base-tooltip
        :message="reasonForDisabling"
      >
        <v-checkbox
          v-model="useRegions"
          :disabled="ertMode"
          label="Use regions?"
        />
      </base-tooltip>
    </v-col>
    <v-col cols="9">
      <choose-parameter
        :disabled="!useRegions || ertMode"
        regular
        parameter-type="region"
        label="Region parameter"
      />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import ChooseParameter from '@/components/selection/dropdown/ChooseParameter.vue'
import WarningDialog from '@/components/dialogs/JobSettings/WarningDialog.vue'
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'

import { Store } from '@/store/typing'
import { NoCache } from '@/utils/helpers'

@Component({
  components: {
    BaseTooltip,
    ChooseParameter,
    WarningDialog,
  },
})
export default class ChooseRegionParameter extends Vue {
  @NoCache
  get useRegions (): boolean {
    return this.$store.state.regions.use
  }

  set useRegions (value: boolean) {
    if (value) {
      (this.$refs.warning as WarningDialog).open(
        'Be aware',
        `
<p>Regions are not, <em>currently</em>, supported in ERT / AHM mode.</p>
<p> You may not use ERT / AHM (in the job settings) while using regions.</p>
`
      )
    }
    this.$store.dispatch('regions/use', { use: value })
  }

  get ertMode (): boolean { return (this.$store as Store).state.fmu.runFmuWorkflows.value }
  get reasonForDisabling (): string {
    if (this.ertMode) {
      return 'ERT / AHM mode is not compatible with regions yet.'
    }
    return ''
  }
}
</script>
