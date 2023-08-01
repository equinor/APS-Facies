<template>
  <v-container
    class="fill-height"
    fluid
  >
    <v-row
      v-if="loading"
    >
      <v-col cols="12">
        <v-row
          justify="center"
          align="center"
        >
          <v-progress-circular
            :size="70"
            indeterminate
          />
        </v-row>
        <v-row
          justify="center"
          align="center"
        >
          <span>{{ loadingMessage }}</span>
        </v-row>
      </v-col>
    </v-row>
    <v-row
      v-else
    >
      <v-col cols="4">
        <scrollable-area>
          <vue-horizontal>
            <selection />
          </vue-horizontal>
        </scrollable-area>
      </v-col>
      <v-col cols="4">
        <scrollable-area>
          <vue-horizontal>
            <preview v-if="hasSimulations" />
          </vue-horizontal>
        </scrollable-area>
      </v-col>
      <v-col cols="4">
        <scrollable-area>
          <vue-horizontal>
            <settings
              v-if="canSpecifyModelSettings"
            />
          </vue-horizontal>
        </scrollable-area>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Selection from '@/components/ElementSelection.vue'
import Settings from '@/components/ElementSettings.vue'
import Preview from '@/components/ElementPreview.vue'
import ScrollableArea from '@/components/baseComponents/ScrollableArea.vue'

import { GaussianRandomField } from '@/utils/domain'

@Component({
  components: {
    ScrollableArea,
    Selection,
    Settings,
    Preview,
  },
})
export default class MainPage extends Vue {
  get canSpecifyModelSettings (): boolean { return this.$store.getters.canSpecifyModelSettings }

  get loading (): boolean { return this.$store.state._loading.value }

  get loadingMessage (): string { return this.$store.state._loading.message }

  get fields (): GaussianRandomField[] { return Object.values(this.$store.getters.fields) }

  get hasSimulations (): boolean { return this.fields.length > 0 }
}
</script>
