<template>
  <v-select
    v-model="conformity"
    :items="options"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Zone } from '@/utils/domain'
import { ZoneConformOption } from '@/utils/domain/zone'

@Component({
})
export default class ConformSelection extends Vue {
  @Prop({ required: true })
  readonly value: Zone

  get conformity (): ZoneConformOption { return this.value.conformity }
  set conformity (value: ZoneConformOption) {
    this.$store.dispatch('zones/conformity', { zone: this.value, value }, { root: true })
  }

  get options () {
    return [
      {
        value: 'TopConform',
        text: 'Top Conform',
      },
      {
        value: 'BaseConform',
        text: 'Base Conform',
      },
      {
        value: 'Proportional',
        text: 'Proportional',
      },
    ]
  }
}
</script>
