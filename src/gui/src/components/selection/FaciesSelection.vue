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
import { Component, Vue } from 'vue-property-decorator'
import FaciesTable from '@/components/table/FaciesTable.vue'

@Component({
  components: {
    FaciesTable,
  },
})
export default class FaciesSelection extends Vue {
  hideAlias: boolean = false

  get hasSelected () { return !!this.$store.state.facies.global.current }

  add () {
    return this.$store.dispatch('facies/global/new', {})
  }

  remove () {
    return this.$store.dispatch('facies/global/removeSelectedFacies')
  }
}
</script>
