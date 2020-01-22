<template>
  <base-selection-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :loading-text="'Loading Facies from RMS'"
    :current.sync="current"
    :no-data-text="noDataText"
    :items="facies"
    :expanded="expanded"
    :select-disabled="!canSelect"
    :select-error="selectFaciesError"
  >
    <template
      v-slot:item="{ item : facies }"
    >
      <td class="text-left">
        <editable-cell
          v-if="!isFaciesFromRms(facies)"
          :value="facies"
          :current="current"
          field="name"
          @submit="changeName"
        />
        <v-popover
          v-else
          trigger="hover"
        >
          <highlight-current-item
            :value="facies"
            :current="current"
            field="name"
          />
          <span slot="popover">{{ 'From RMS' }}</span>
        </v-popover>
      </td>
      <td
        v-if="!hideAlias"
        class="text-left"
      >
        <editable-cell
          :value="facies"
          :current="current"
          field="alias"
          @submit="changeAlias"
        />
      </td>
      <td class="text-left">
        <highlight-current-item
          v-if="blockedWellLogParameter"
          :value="facies"
          :current="current"
          field="code"
        />
        <editable-cell
          v-else
          :value="facies"
          :current="current"
          field="code"
          numeric
          @submit="changeCode"
        />
      </td>
      <td
        :style="{backgroundColor: facies.color}"
        @click.stop="() => changeColorSelection(facies)"
      />
    </template>
    <template
      v-slot:expanded-item="{ item, headers }"
    >
      <td
        :colspan="headers.length"
      >
        <swatches
          :value="item.color"
          :colors="availableColors"
          inline
          swatches-size="30"
          @input="color => changeColor(item, color)"
        />
      </td>
    </template>
  </base-selection-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

// eslint-disable-next-line @typescript-eslint/ban-ts-ignore
// @ts-ignore
import Swatches from 'vue-swatches'
import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import EditableCell from '@/components/table/EditableCell.vue'
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'

import { Facies, GlobalFacies, Parent } from '@/utils/domain'
import { RootGetters, RootState } from '@/store/typing'
import { Color } from '@/utils/domain/facies/helpers/colors'
import { HeaderItems } from '@/utils/typing'

import { hasCurrentParents } from '@/utils'

@Component({
  components: {
    BaseSelectionTable,
    OptionalHelpItem,
    HighlightCurrentItem,
    Swatches,
    EditableCell,
  }
})
export default class FaciesTable extends Vue {
  @Prop({ default: false, type: Boolean })
  readonly hideAlias!: boolean

  expanded: Facies[] = []

  get canSelect (): boolean { return this.$store.getters.canSpecifyModelSettings }

  get loading (): boolean { return this.$store.state.facies.global._loading }

  get current (): GlobalFacies { return this.$store.state.facies.global.current }
  set current ({ id }: GlobalFacies) { this.$store.dispatch('facies/global/current', { id }) }

  get noDataText (): string {
    return this.loading
      ? 'Loading facies table from RMS'
      : 'There are no facies for the selected well logs. You may still add new facies.'
  }

  get facies (): Facies[] { return this.$store.getters.faciesTable }

  get parent (): Parent {
    const state = this.$store.state
    return {
      zone: state.zones.current,
      region: state.regions.current
    }
  }

  get headers (): HeaderItems {
    return [
      {
        text: 'Use',
        value: 'selected',
      },
      {
        text: 'Facies',
        value: 'name',
      },
      ...(this.hideAlias ? [] : [
        {
          text: 'Alias',
          value: 'alias'
        },
      ]),
      {
        text: 'Code',
        sortable: true,
        value: 'code',
      },
      {
        text: 'Color',
        value: 'color',
      },
    ]
  }

  get selected (): GlobalFacies[] {
    const state: RootState = this.$store.state
    const getters: RootGetters = this.$store.getters
    return Object.values(state.facies.global.available)
      .filter(facies => Object.values(state.facies.available)
        .filter(facies => hasCurrentParents(facies, getters))
        .findIndex(localFacies => localFacies.facies.id === facies.id) >= 0)
  }

  set selected (value) { this.$store.dispatch('facies/select', { items: value, parent: this.parent }) }

  get availableColors (): Color[] { return this.$store.getters['constants/faciesColors/available'] }

  get selectFaciesError (): string {
    const item = this.$store.state.regions.use && !this.parent.region
      ? 'Region'
      : 'Zone'
    return !this.canSelect
      ? `A ${item} must be selected, before including a facies in the model`
      : ''
  }

  get blockedWellLogParameter (): boolean {
    return !!this.$store.getters.blockedWellLogParameter
  }

  isFaciesFromRms (facies: GlobalFacies): boolean {
    return this.$store.getters['facies/isFromRMS'](facies)
  }

  async changeColor (facies: GlobalFacies, color: string): Promise<void> {
    if (facies.color !== color) {
      // Only dispatch when the color *actually* changes
      await this.$store.dispatch('facies/global/changeColor', { id: facies.id, color })
    }
  }

  async changeName (facies: GlobalFacies): Promise<void> {
    await this.$store.dispatch('facies/global/changeName', { id: facies.id, name: facies.name || `F${facies.code}` })
  }

  async changeAlias (facies: GlobalFacies): Promise<void> {
    await this.$store.dispatch('facies/global/changeAlias', facies)
  }

  async changeCode (facies: GlobalFacies): Promise<void> {
    await this.$store.dispatch('facies/global/changeCode', facies)
  }

  changeColorSelection (facies: Facies): void {
    const previous = this.expanded.pop()
    if (previous && previous.id === facies.id) {
      this.expanded = []
    } else {
      this.expanded = [facies]
    }
  }
}
</script>
