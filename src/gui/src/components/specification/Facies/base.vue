<template>
  <v-select
    :items="faciesOptions"
    :value="selected"
    :clearable="clearable"
    @input.capture="facies => $emit('input', facies)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'
import { getId } from '@/utils/helpers'

import { Store } from '@/store/typing'
import { ID } from '@/utils/domain/types'
import Facies from '@/utils/domain/facies/local'
import { ListItem } from '@/utils/typing'

@Component
export default class FaciesSpecificationBase extends Vue {
  @Prop({ required: true })
  readonly value: Facies | ID | Facies[] | ID[]

  @Prop({ default: false })
  readonly disable: ((facies: Facies) => boolean) | boolean

  @Prop({ default: false, type: Boolean })
  readonly clearable!: boolean

  get selectedFacies (): Facies[] {
    return (this.$store as Store).getters['facies/selected']
  }

  get selected (): ID | ID[] {
    if (Array.isArray(this.value)) return (this.value as ID[]).map(getId)
    return getId(this.value)
  }

  get faciesOptions (): ListItem<string>[] {
    return this.selectedFacies
      .map(facies => {
        return {
          text: facies.alias,
          value: facies.id,
          disabled: this.disable instanceof Function ? this.disable(facies) : this.disable,
        }
      })
  }
}
</script>
