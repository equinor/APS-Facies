<template>
  <div>
    <confirmation-dialog
      v-if="warn"
      ref="confirm"
    />
    <v-select
      ref="selection"
      v-model.lazy="selected"
      :items="items"
      :disabled="disabled"
      :label="label"
    >
      <template v-slot:item="{ item, on }">
        <v-list-item
          v-on="on"
        >
          <v-hover
            v-slot:default="{ hover }"
            class="pa-0 ma-0"
          >
            <base-tooltip
              v-if="item.help"
              :message="item.help"
              :open="hover"
              :disabled="!item.disabled && !item.help"
              trigger="manual"
            >
              <span
                :style="itemStyle(item)"
              >
                {{ item.text }}
              </span>
            </base-tooltip>
            <span
              v-else
              :style="itemStyle(item)"
            >
              {{ item.text }}
            </span>
          </v-hover>
        </v-list-item>
      </template>
    </v-select>
  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/ban-ts-comment */
import { Component, Prop, Vue } from 'vue-property-decorator'

import ConfirmationDialog from '@/components/specification/GaussianRandomField/ConfirmationDialog.vue'
import BaseTooltip from '@/components/baseComponents/BaseTooltip.vue'

import { ListItem } from '@/utils/typing'

@Component({
  components: {
    BaseTooltip,
    ConfirmationDialog,
  },
})
export default class BaseDropdown<T> extends Vue {
  @Prop({ required: true })
  readonly value!: T

  @Prop({ required: true })
  readonly label!: string

  @Prop({ required: true })
  readonly items!: ListItem<T>[]

  @Prop({ default: false })
  readonly disabled!: boolean

  @Prop({ default: false, type: Boolean })
  readonly warn!: boolean

  @Prop({ default: '' })
  readonly warnMessage!: string

  @Prop({ default: false, type: Boolean })
  readonly warnEvenWhenEmpty: boolean

  get selected (): T { return this.value }
  set selected (value: T) {
    const changeValue = (): void => { this.$emit('input', value) }

    if (this.warn && (!!this.selected || this.warnEvenWhenEmpty)) {
      // @ts-ignore
      (this.$refs.confirm as ConfirmationDialog).open('Are you sure?', this.warnMessage)
        .then((confirmed: boolean) => {
          if (confirmed) changeValue()
          else {
            // The component must be made aware that its value was not updated
            // @ts-ignore
            this.$refs.selection.lazyValue = this.selected
          }
        })
    } else {
      changeValue()
    }
  }

  itemStyle (item: ListItem<T>): Partial<CSSStyleDeclaration> {
    if (item.disabled) {
      return {
        color: 'rgba(0, 0, 0, 0.38)',
      }
    }
    return {}
  }
}
</script>
