<template>
  <v-layout
    column
  >
    <v-layout
      row
      fill-height
      justify-start
    >
      <v-flex xs2>
        <v-btn
          icon
          @click="add"
        >
          <v-icon>{{ $vuetify.icons.add }}</v-icon>
        </v-btn>
      </v-flex>
      <v-flex xs2>
        <v-popover
          :disabled="canRemove"
          trigger="hover"
        >
          <v-btn
            icon
            :disabled="!canRemove"
            @click="remove"
          >
            <v-icon>{{ $vuetify.icons.remove }}</v-icon>
          </v-btn>
          <span slot="popover">
            {{ removeError }}
          </span>
        </v-popover>
      </v-flex>
      <v-flex xs8 />
    </v-layout>
    <facies-table :hide-alias="hideAlias" />
  </v-layout>
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

  get current () { return (this.$store as Store).getters.facies }

  get canRemove () {
    return (
      this.current
        ? !this.$store.getters['facies/isFromRMS'](this.current)
        : false
    )
  }

  get removeError () {
    if (!this.current) return 'A facies must be selected'
    if (!this.canRemove) return `The selected facies, ${this.current.name}, is from RMS, and cannot be deleted from this GUI`
    return ''
  }

  add () {
    return this.$store.dispatch('facies/global/new', {})
  }

  remove () {
    return this.$store.dispatch('facies/global/removeSelectedFacies')
  }
}
</script>
