<template>
  <base-selection-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="loadingText"
    :items="items"
    :no-data-text="_noDataText"
    :current.sync="current"
  >
    <template
      v-slot:item="{ item }"
    >
      <td
        v-if="showName"
        class="text-start"
      >
        {{ item.name }}
      </td>
      <td
        v-if="showCode"
        class="text-start"
      >
        {{ item.code }}
      </td>
      <td
        v-if="showConformity"
        class="text-start"
      >
        <conform-selection
          :value="item"
        />
      </td>
      <td>
        <v-row
          justify="center"
          align="center"
        >
          <icon-button
            icon="copy"
            :color="getColor(item)"
            @click="() => copy(item)"
          />
          <icon-button
            v-if="source"
            icon="paste"
            loading-spinner
            :disabled="!canPaste(item)"
            :waiting="isPasting(item)"
            @click="() => paste(item)"
          />
        </v-row>
      </td>
    </template>
  </base-selection-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'
import IconButton from '@/components/selection/IconButton.vue'
import ConformSelection from '@/components/selection/dropdown/ConformSelection.vue'

import SelectableItem from '@/utils/domain/bases/selectableItem'

import { getId } from '@/utils'

import { HeaderItems } from '@/utils/typing'

@Component({
  components: {
    ConformSelection,
    BaseSelectionTable,
    IconButton,
  },
})
export default class SelectionTable<T extends SelectableItem> extends Vue {
  @Prop({ required: true })
  readonly headerName!: string

  @Prop({ required: true })
  readonly itemType!: 'zone' | 'region'

  @Prop({ default: '$vuetify.noDataText' })
  readonly noDataText!: string

  @Prop({ default: false, type: Boolean })
  readonly showName!: boolean

  @Prop({ default: false, type: Boolean })
  readonly showCode!: boolean

  @Prop({ default: '$vuetify.dataIterator.loadingText' })
  readonly loadingText!: string

  get _noDataText (): string {
    return this.loading
      ? `Loading ${this.itemType}s`
      : this.noDataText
  }

  get loading (): boolean { return this.$store.state[`${this.itemType}s`]._loading }

  get headers (): HeaderItems {
    return [
      {
        text: 'Use',
        value: 'selected',
      },
      ...(this.showName
        ? [{
          text: this.headerName,
          value: 'name',
        }]
        : []
      ),
      ...(this.showCode
        ? [{
          text: 'Code',
          sortable: true,
          value: 'code',
        }]
        : []
      ),
      ...(this.showConformity
        ? [{
          text: 'Conformity',
          value: 'conformity',
        }]
        : []
      ),
      {
        text: 'Copy/Paste',
      },
    ]
  }

  get items (): T[] {
    return this.$store.getters[`${this.itemType}s`]
      .sort((a: T, b: T) => a.code - b.code)
  }

  get current (): T { return this.$store.state[`${this.itemType}s`].current }
  set current (item: T) { this.$store.dispatch(`${this.itemType}s/current`, item) }

  get selected (): T[] { return this.items.filter(item => !!item.selected) }
  set selected (values) {
    values = this.items.filter(item => values.map(({ id }) => id).includes(item.id))
    this.$store.dispatch(`${this.itemType}s/select`, values)
  }

  get source (): T {
    return this.$store.state.copyPaste.source
  }

  get showConformity (): boolean { return this.$store.getters.fmuMode && this.itemType === 'zone' }

  getItem (item: T): T | undefined { return this.items.find(({ id }) => id === item.id) }

  getColor (item: T): 'accent' | undefined {
    return getId(this.source) === item.id
      ? 'accent'
      : undefined
  }

  canPaste (item: T): boolean {
    const source = this.source
    return !!source && source.id !== item.id
  }

  isPasting (item: T): boolean {
    return !!this.$store.getters['copyPaste/isPasting'](this.getItem(item))
  }

  async copy (item: T): Promise<void> {
    await this.$store.dispatch('copyPaste/copy', this.getItem(item))
  }

  async paste (item: T): Promise<void> {
    await this.$store.dispatch('copyPaste/paste', this.getItem(item))
  }

  updateSelection (item: T, value: boolean): void {
    if (value) {
      this.selected = [...this.selected, item]
    } else {
      this.selected = this.selected.filter(el => el.id !== item.id)
    }
  }
}
</script>

<style lang="scss" scoped>
  div {
    flex-wrap: nowrap;
  }
</style>
