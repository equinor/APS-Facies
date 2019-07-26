<template>
  <span
    :class="isCurrent ? 'font-weight-bold' : ''"
  >
    {{ value[field] }}
  </span>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseItem from '@/utils/domain/bases/baseItem'
import { ID } from '@/utils/domain/types'

@Component
export default class HighlightCurrentItem<T extends BaseItem> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly field!: string

  @Prop({ default: undefined })
  readonly current!: ID | undefined

  get isCurrent () { return this.value.id === this.current }
}
</script>
