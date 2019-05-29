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
      ]
    },
    items () {
      const current = this.$store.state[`${this.itemType}s`].current
      return this.$store.getters[`${this.itemType}s`]
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
    }
  },

  methods: {
    current (id) {
      this.$store.dispatch(`${this.itemType}s/current`, { id })
    }
  }

}
</script>
