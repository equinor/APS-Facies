<template>
  <v-data-table
    v-model="selected"
    :headers="headers"
    :loading="loading"
    :items="items"
    :no-data-text="_noDataText"
    must-sort
    item-key="id"
    class="elevation-1"
    hide-actions
  >
    <template
      slot="headerCell"
      slot-scope="props"
    >
      <optional-help-item
        :value="props.header"
      />
    </template>
    <template
      slot="items"
      slot-scope="props"
    >
      <tr
        :style="props.item.current ? selectedStyle : ''"
        @click="() => current(props.item.id)"
      >
        <td>
          <v-checkbox
            v-model="props.selected"
            :indeterminate="props.item.selected === 'intermediate'"
            primary
            hide-details
          />
        </td>
        <td
          v-if="showName"
          class="text-xs-left"
        >
          <highlight-current-item
            :item="props.item"
            field="name"
          />
        </td>
        <td
          v-if="showCode"
          class="text-xs-left"
        >
          {{ props.item.code }}
        </td>
        <td>
          <v-layout row>
            <icon-button
              icon="copy"
              :color="getColor(props.item)"
              @click="() => copy(props.item)"
            />
            <icon-button
              v-if="source"
              icon="paste"
              loading-spinner
              :disabled="!canPaste(props.item)"
              :waiting="isPasting(props.item)"
              @click="() => paste(props.item)"
            />
          </v-layout>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import VueTypes from 'vue-types'

import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import IconButton from '@/components/selection/IconButton'

import { getId } from '@/utils'

export default {
  components: {
    IconButton,
    OptionalHelpItem,
    HighlightCurrentItem,
  },

  props: {
    headerName: {
      required: true,
      type: String,
    },
    itemType: {
      required: true,
      type: String,
    },
    noDataText: VueTypes.string.def('$vuetify.noDataText'),
    showName: VueTypes.bool.def(false),
    showCode: VueTypes.bool.def(false),
  },

  computed: {
    _noDataText () {
      return this.loading
        ? `Loading ${this.itemType}s`
        : this.noDataText
    },
    loading () {
      return this.$store.state[`${this.itemType}s`]._loading
    },
    headers () {
      return [
        {
          text: 'Use',
          align: 'left',
          sortable: false,
          value: 'selected',
        },
        ...(this.showName
          ? [{
            text: this.headerName,
            align: 'left',
            sortable: false,
            value: 'name',
          }]
          : []
        ),
        ...(this.showCode
          ? [{
            text: 'Code',
            align: 'left',
            sortable: true,
            value: 'code',
          }]
          : []
        ),
        {
          text: 'Copy/Paste',
          align: 'left',
          sortable: false,
        },
      ]
    },
    _items () { return this.$store.getters[`${this.itemType}s`] },
    items () {
      const current = this.$store.state[`${this.itemType}s`].current
      return this._items
        .map(item => {
          return {
            id: item.id,
            name: item.name,
            code: item.code,
            selected: item.selected,
            current: item.id === current,
          }
        })
    },
    selected: {
      get: function () { return this.items.filter(item => item.selected) },
      set: function (values) {
        values = this.$store.getters[`${this.itemType}s`].filter(item => values.map(({ id }) => id).includes(item.id))
        this.$store.dispatch(`${this.itemType}s/select`, values)
      },
    },
    selectedStyle () {
      return {
        background: this.$vuetify.theme.primary,
        color: 'white'
      }
    },
    source () {
      return this.$store.state.copyPaste.source
    }
  },

  methods: {
    current (id) {
      this.$store.dispatch(`${this.itemType}s/current`, { id })
    },
    getItem (item) {
      return this._items.find(({ id }) => id === item.id)
    },
    getColor (item) {
      return getId(this.source) === item.id
        ? 'accent'
        : undefined
    },
    canPaste (item) {
      const source = this.source
      return !!source && source.id !== item.id
    },
    isPasting (item) {
      return !!this.$store.getters['copyPaste/isPasting'](this.getItem(item))
    },
    async copy (item) {
      await this.$store.dispatch('copyPaste/copy', this.getItem(item))
    },
    async paste (item) {
      await this.$store.dispatch('copyPaste/paste', this.getItem(item))
    }
  }

}
</script>
