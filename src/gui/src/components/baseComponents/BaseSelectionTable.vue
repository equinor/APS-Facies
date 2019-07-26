<template>
  <base-table
    :value="value"
    :headers="headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="noDataText"
    :expanded="expanded"
  >
    <template
      v-slot:item="{ item, isSelected, on }"
    >
      <tr
        :style="isCurrent(item) ? selectedStyle : ''"
        @click="() => propagateCurrent(item)"
        v-on="on"
      >
        <td>
          <v-popover
            :disabled="!selectDisabled"
            trigger="hover"
          >
            <v-checkbox
              :style="{ marginTop: 0 }"
              :value="isSelected"
              :input-value="!_isIndeterminate(item) && isSelected"
              :indeterminate="_isIndeterminate(item)"
              :disabled="selectDisabled"
              primary
              hide-details
              @change="e => updateSelection(item, e)"
            />
            <span slot="popover">
              {{ selectError }}
            </span>
          </v-popover>
        </td>
        <slot
          :item="item"
          :isSelected="isSelected"
          :on="on"
          name="item"
        />
      </tr>
    </template>
    <template
      v-slot:expanded-item="{ item, headers }"
    >
      <slot
        :item="item"
        :headers="headers"
        name="expanded-item"
      />
    </template>
  </base-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseTable from '@/components/baseComponents/BaseTable.vue'
import BaseItem from '@/utils/domain/bases/baseItem'
import SelectableItem from '@/utils/domain/bases/selectableItem'
import { ID } from '@/utils/domain/types'

interface Header {
  text: string
  align?: string
  sortable?: boolean
  value: string
}

@Component({
  components: {
    BaseTable,
  },
})
export default class SelectionTable<T extends BaseItem> extends Vue {
  @Prop({ required: true })
  readonly value!: T[]

  @Prop({ required: true })
  readonly headers!: Header[]

  @Prop({ required: true })
  readonly items!: T[]

  @Prop({ default: undefined })
  readonly current!: ID | undefined

  @Prop({ default: () => [] })
  readonly expanded: number[]

  @Prop({ default: false, type: Boolean })
  readonly loading!: boolean

  @Prop({ default: '$vuetify.dataIterator.loadingText' })
  readonly loadingText!: string

  @Prop({ default: '$vuetify.noDataText' })
  readonly noDataText!: string

  @Prop({ default: false, type: Boolean })
  readonly selectDisabled!: boolean

  @Prop({ default: undefined })
  readonly selectError!: string | undefined

  get selectedStyle () {
    return {
      background: this.$vuetify.theme.themes.light.primary,
      color: 'white',
    }
  }

  isCurrent (item: T): boolean {
    if (!this.current) return false
    return item.id === this.current
  }
  propagateCurrent (item: T) {
    this.$emit('update:current', item)
  }
  updateSelection (item: T, value: boolean): void {
    if (value) {
      this.$emit('input', [...this.value, item])
    } else {
      this.$emit('input', this.value.filter(el => el.id !== item.id))
    }
  }

  _isIndeterminate (item: T): boolean {
    return item instanceof SelectableItem
      ? item.selected === 'intermediate'
      : false
  }
}
</script>
