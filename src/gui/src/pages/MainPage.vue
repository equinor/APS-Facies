<template>
  <v-container
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
      no-gutters
    >
      <v-col cols="4">
        <selection />
      </v-col>
      <v-col cols="4">
        <preview v-if="hasSimulations" />
      </v-col>
      <v-col cols="4">
        <settings
          v-if="canSpecifyModelSettings"
        />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Selection from '@/components/ElementSelection.vue'
import Settings from '@/components/ElementSettings.vue'
import Preview from '@/components/ElementPreview.vue'

import { GaussianRandomField } from '@/utils/domain'

@Component({
  components: {
    Selection,
    Settings,
    Preview
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
