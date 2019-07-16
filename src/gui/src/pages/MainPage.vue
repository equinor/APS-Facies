<template>
  <v-container fluid>
    <v-layout
      v-if="loading"
      column
      align-center
      justify-center
      fill-height
    >
      <v-flex />
      <v-flex>
        <v-progress-circular
          :size="70"
          indeterminate
        />
      </v-flex>
      <v-flex>
        <span>{{ loadingMessage }}</span>
      </v-flex>
      <v-flex />
    </v-layout>
    <v-layout
      v-else
      wrap
    >
      <v-flex xs4>
        <selection />
      </v-flex>
      <v-flex xs4>
        <preview v-if="hasSimulations" />
      </v-flex>
      <v-flex xs4>
        <settings
          v-if="canSpecifyModelSettings"
        />
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

import Selection from '@/components/ElementSelection.vue'
import Settings from '@/components/ElementSettings.vue'
import Preview from '@/components/ElementPreview.vue'

@Component({
  components: {
    Selection,
    Settings,
    Preview
  },
})
export default class MainPage extends Vue {
  get canSpecifyModelSettings () { return this.$store.getters['canSpecifyModelSettings'] }

  get loading () { return this.$store.state._loading.value }

  get loadingMessage () { return this.$store.state._loading.message }

  get fields () { return Object.values(this.$store.getters.fields) }

  get hasSimulations () { return this.fields.length > 0 }
}
</script>
