<template>
  <v-data-table
    v-model="selected"
    :headers="headers"
    :items="items"
    :no-data-text="noDataText"
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
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import VueTypes from 'vue-types'

import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'

export default {
  components: {
    OptionalHelpItem,
    HighlightCurrentItem,
  },

  props: {
    headerName: VueTypes.string.isRequired,
    itemType: VueTypes.string.isRequired,
    noDataText: VueTypes.string.def('$vuetify.noDataText'),
    showName: VueTypes.bool.def(false),
    showCode: VueTypes.bool.def(false),
  },

  computed: {
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
      ]
    },
    items () {
      const state = this.$store.state[`${this.itemType}s`]
      const items = state.available
      return Object.keys(items)
        .map(id => {
          const item = items[`${id}`]
          return {
            id,
            name: item.name,
            code: item.code,
            selected: item.selected,
            current: id === state.current,
          }
        })
    },
    selected: {
      get: function () { return Object.values(this.items).filter(item => item.selected) },
      set: function (value) { this.$store.dispatch(`${this.itemType}s/select`, value) },
    },
    selectedStyle () {
      return {
        background: this.$vuetify.theme.info,
        color: 'white'
      }
    }
  },

  methods: {
    current (id) {
      this.$store.dispatch(`${this.itemType}s/current`, { id })
    }
  }

}
</script>
