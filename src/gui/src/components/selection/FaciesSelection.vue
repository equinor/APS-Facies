<template>
  <v-flex>
    <v-flex>
      <v-btn
        icon
        @click="add"
      >
        <v-icon>{{ $vuetify.icons.add }}</v-icon>
      </v-btn>
      <v-btn
        icon
        :disabled="!hasSelected"
        @click="remove"
      >
        <v-icon>{{ $vuetify.icons.remove }}</v-icon>
      </v-btn>
    </v-flex>
    <facies-table :hide-alias="hideAlias" />
  </v-flex>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import FaciesTable from '@/components/table/FaciesTable.vue'

import { Store } from '@/store/typing'

@Component({
  components: {
    FaciesTable,
  },
})
export default class FaciesSelection extends Vue {
  @Prop({ default: false, type: Boolean })
  readonly hideAlias: boolean

  get hasSelected () { return !!(this.$store as Store).state.facies.global.current }

  add () {
    return this.$store.dispatch('facies/global/new', {})
  }

  remove () {
    return this.$store.dispatch('facies/global/removeSelectedFacies')
  }
}
</script>
