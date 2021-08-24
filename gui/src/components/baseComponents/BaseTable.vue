<template>
  <v-data-table
    :value="value"
    :headers="_headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="noDataText"
    :expanded="expanded"
    :custom-sort="customSort"
    :dense="dense"
    must-sort
    item-key="id"
    :class="`elevation-${elevation}`"
    :items-per-page="Infinity"
    hide-default-footer
    hide-default-header
  >
    <template
      #header="{ props: { headers } }"
    >
      <thead>
        <tr>
          <th
            v-for="header in headers"
            :key="header.name"
          >
            <optional-help-item
              :value="header"
            />
          </th>
        </tr>
      </thead>
    </template>
    <template
      #item="{ item, isSelected, on }"
    >
      <slot
        :item="item"
        :isSelected="isSelected"
        :on="on"
        name="item"
      />
    </template>
    <template
      #expanded-item="{ item, headers }"
    >
      <slot
        :item="item"
        :headers="headers"
        name="expanded-item"
      />
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'

import BaseItem from '@/utils/domain/bases/baseItem'
import { ID } from '@/utils/domain/types'
import { DataTableCompareFunction } from 'vuetify/types'
import { HeaderItems } from '@/utils/typing'

@Component({
  components: {
    OptionalHelpItem,
  },
})
export default class SelectionTable<T extends BaseItem> extends Vue {
  @Prop({ required: false, default: () => [] })
  readonly value!: T[]

  @Prop({ required: true })
  readonly headers!: HeaderItems

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

  @Prop({ default: '1' })
  readonly elevation: string

  @Prop({ default: undefined })
  readonly customSort!: ((items: T[], sortBy: string[], sortDesc: boolean[], locale: string, customSorters?: Record<string, DataTableCompareFunction>) => T[]) | undefined

  @Prop({ default: false, type: Boolean })
  readonly dense!: boolean

  get _headers (): HeaderItems {
    return this.headers
      .map(header => {
        return {
          align: 'left',
          sortable: false,
          ...header,
        }
      })
  }
}
</script>
