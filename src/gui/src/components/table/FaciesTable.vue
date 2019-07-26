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
      v-slot:item="{ item, expand }"
    >
      <td class="text-left">
        <v-edit-dialog
          v-if="!isFaciesFromRms(item)"
          lazy
        >
          <highlight-current-item
            :value="item"
            :current="current"
            field="name"
          />
          <v-text-field
            slot="input"
            v-model="item.name"
            label="Edit"
            single-line
            @keydown.enter="() => changeName(item)"
          />
        </v-edit-dialog>
        <v-popover
          v-else
          trigger="hover"
        >
          <highlight-current-item
            :value="item"
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
        <v-edit-dialog
          lazy
        >
          <highlight-current-item
            :value="item"
            :current="current"
            field="alias"
          />
          <v-text-field
            slot="input"
            v-model="item.alias"
            label="Edit"
            single-line
            @keydown.enter="() => changeAlias(item)"
          />
        </v-edit-dialog>
      </td>
      <td class="text-left">
        <highlight-current-item
          :value="item"
          :current="current"
          field="code"
        />
      </td>
      <td
        :style="{backgroundColor: item.color}"
        @click.stop="() => changeColorSelection(item)"
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

// @ts-ignore
import Swatches from 'vue-swatches'
import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import BaseSelectionTable from '@/components/baseComponents/BaseSelectionTable.vue'

import { Facies, GlobalFacies } from '@/utils/domain'
import { ID } from '@/utils/domain/types'
import { RootGetters, RootState } from '@/store/typing'

import { hasCurrentParents } from '@/utils'

@Component({
  components: {
    BaseSelectionTable,
    OptionalHelpItem,
    HighlightCurrentItem,
    Swatches,
  }
})
export default class FaciesTable extends Vue {
  @Prop({ default: false, type: Boolean })
  readonly hideAlias!: boolean

  expanded: Facies[] = []

  get canSelect () { return this.$store.getters['canSpecifyModelSettings'] }

  get loading () { return this.$store.state.facies.global._loading }

  get current () { return this.$store.state.facies.global.current }
  set current ({ id }: { id: ID }) { this.$store.dispatch('facies/global/current', { id }) }

  get noDataText () {
    return this.loading
      ? 'Loading facies table from RMS'
      : 'There are no facies for the selected well logs'
  }

  get facies () { return this.$store.getters['faciesTable'] }

  get parent () {
    const state = this.$store.state
    return {
      zone: state.zones.current,
      region: state.regions.current
    }
  }
  get headers () {
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
  get selected () {
    const state: RootState = this.$store.state
    const getters: RootGetters = this.$store.getters
    return Object.values(state.facies.global.available)
      .filter(facies => Object.values(state.facies.available)
        .filter(facies => hasCurrentParents(facies, getters))
        .findIndex(localFacies => localFacies.facies.id === facies.id) >= 0)
  }
  set selected (value) { this.$store.dispatch('facies/select', { items: value, parent: this.parent }) }

  get availableColors () { return this.$store.state.constants.faciesColors.available }

  get selectFaciesError () {
    const item = this.$store.state.regions.use && !this.parent.region
      ? 'Region'
      : 'Zone'
    return !this.canSelect
      ? `A ${item} must be selected, before including a facies in the model`
      : ''
  }

  isFaciesFromRms (facies: GlobalFacies) {
    return this.$store.getters['facies/isFromRMS'](facies)
  }

  async changeColor (facies: GlobalFacies, color: string) {
    if (facies.color !== color) {
      // Only dispatch when the color *actually* changes
      await this.$store.dispatch('facies/global/changeColor', { id: facies.id, color })
    }
  }

  changeName (facies: GlobalFacies) {
    return this.$store.dispatch('facies/global/changeName', { id: facies.id, name: facies.name || `F${facies.code}` })
  }

  changeAlias (facies: GlobalFacies) {
    return this.$store.dispatch('facies/global/changeAlias', { id: facies.id, alias: facies.alias })
  }

  changeColorSelection (facies: Facies) {
    const previous = this.expanded.pop()
    if (previous && previous.id === facies.id) {
      this.expanded = []
    } else {
      this.expanded = [facies]
    }
  }
}
</script>
