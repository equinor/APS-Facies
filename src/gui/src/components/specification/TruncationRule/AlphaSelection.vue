<template>
  <v-select
    v-model="selected"
    :items="fields"
    clearable
  >
    <template
      v-if="channel"
      slot="label"
    >
      <span>α<sub>{{ channel }}</sub></span>
    </template>
  </v-select>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { GaussianRandomField } from '@/utils/domain'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'
import TruncationRule from '@/utils/domain/truncationRule/base'
import Polygon from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'

@Component
export default class AlphaSelection extends Vue {
  @Prop({ required: true })
  readonly value!: GaussianRandomField | null

  @Prop({ required: true })
  readonly rule!: TruncationRule<Polygon>

  @Prop({ default: 0 })
  readonly channel: number

  @Prop({ default: '' })
  readonly group: ID

  get _fields (): GaussianRandomField[] { return this.$store.getters['fields'] }

  get id (): ID | '' { return this.value ? this.value.id : '' }

  get selected (): ID | null {
    if (this.value instanceof GaussianRandomField) {
      if (this.fields.find(item => item.value === (this.value as GaussianRandomField).id)) {
        return this.value.id
      }
    }
    return null
  }
  set selected (value) { this.$emit('input', value) }

  get fields () {
    return Object.values(this._fields)
      .map(field => {
        /* Is background field, and is not in the same location */
        let disabled = this.rule.isUsedInDifferentAlpha(this.id, this.channel)

        /* Are we dealing with a field used in overlay? */
        if (this.rule instanceof OverlayTruncationRule) {
          if (this.group) {
            if (this.rule.isUsedInBackground(field)) {
              /* This field is background field */
              disabled = true
            } else {
              /* This field  MAY be used in overlay */
              disabled = (
                /* A Gaussian Field CANNOT be used twice in the same group */
                this.rule.isUsedInDifferentOverlayPolygon(this.group, field)
                /* A Gaussian Field used in overlay, CANNOT be used in the background, and vice versa */
                || this.rule.isUsedInBackground(field)
              )
            }
          } else {
            /* This field MAY have been used in overlay */
            disabled = this.rule.isUsedInOverlay(field)
          }
        }
        if (this.value) {
          /* A field that is CURRENTLY selected, should never be disabled */
          disabled = disabled && this.value.id !== field.id
        }
        return {
          text: field.name,
          value: field.id,
          disabled,
        }
      })
  }
}
</script>
