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

<script>
import { mapGetters } from 'vuex'

import Selection from '@/components/ElementSelection'
import Settings from '@/components/ElementSettings'
import Preview from '@/components/ElementPreview'

export default {
  components: {
    Selection,
    Settings,
    Preview
  },

  computed: {
    ...mapGetters([
      'canSpecifyModelSettings',
    ]),
    loading () {
      return this.$store.state._loading.value
    },
    loadingMessage () {
      return this.$store.state._loading.message
    },
    fields () {
      return Object.values(this.$store.getters.fields)
    },
    hasSimulations () {
      return this.fields.length > 0
    },
  }
}
</script>
