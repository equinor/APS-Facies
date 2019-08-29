<template>
  <v-row
    no-gutters
  >
    <v-row
      class="fill-height"
      justify="start"
    >
      <v-col cols="2">
        <icon-button
          icon="add"
          @click="add"
        />
      </v-col>
      <v-col cols="2">
        <v-popover
          :disabled="canRemove"
          trigger="hover"
        >
          <icon-button
            icon="remove"
            :disabled="!canRemove"
            @click="remove"
          />
          <span slot="popover">
            {{ removeError }}
          </span>
        </v-popover>
      </v-col>
      <v-col cols="8" />
    </v-row>
    <v-col cols="12">
      <facies-table :hide-alias="hideAlias" />
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import FaciesTable from '@/components/table/FaciesTable.vue'
import IconButton from '@/components/selection/IconButton.vue'

import { Store } from '@/store/typing'

@Component({
  components: {
    IconButton,
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
