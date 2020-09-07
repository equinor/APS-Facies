<template>
  <base-tooltip
    :message="active ? message : inactiveMessage"
  >
    <v-icon
      :color="color"
    >
      {{ __icon }}
    </v-icon>
  </base-tooltip>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'
import { GlobalFacies } from '@/utils/domain'
import { ID } from '@/utils/domain/types'
import { VuetifyIcon } from 'vuetify/types/services/icons'

@Component({
  components: {
    BaseTooltip,
  },
})
export default class InformationalIcon extends Vue {
  @Prop({ required: true })
  readonly value!: GlobalFacies

  @Prop({ required: true })
  readonly icon!: string

  @Prop({ default: undefined })
  readonly current?: ID

  @Prop({ default: false, type: Boolean })
  readonly active!: boolean

  @Prop({ default: undefined })
  readonly message?: string

  @Prop({ default: undefined })
  readonly inactiveMessage?: string

  // eslint-disable-next-line @typescript-eslint/naming-convention
  get __icon (): VuetifyIcon | undefined {
    const icons = this.$vuetify.icons.values
    const iconName = `${this.icon}${!this.active ? 'Negated' : ''}`
    return icons[`${iconName}`]
  }

  get isCurrent (): boolean { return this.current === this.value.id }

  get color (): string | undefined { return this.isCurrent ? 'white' : undefined }
}
</script>
