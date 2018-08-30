<template>
  <v-data-table
    :headers="headers"
    :items="items"
    :no-data-text="noDataText"
    v-model="selected"
    item-key="name"
    select-all
    class="elevation-1"
    hide-actions
  >
    <template
      slot="headerCell"
      slot-scope="props"
    >
      <v-tooltip bottom>
        <span slot="activator">
          {{ props.header.text }}
        </span>
        <span>
          {{ props.header.text }}
        </span>
      </v-tooltip>
    </template>
    <template
      slot="items"
      slot-scope="props"
    >
      <tr @click="() => current(props.item.id)">
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
          <span :class="props.item.current ? 'font-weight-bold' : ''">{{ props.item.itemName }}</span>
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

export default {
  props: {
    headerName: VueTypes.string.isRequired,
    itemType: VueTypes.string.isRequired,
    noDataText: VueTypes.string.def('$vuetify.noDataText'),
    showName: VueTypes.bool.def(false),
    showCode: VueTypes.bool.def(false),
  },

  data () {
    return {
      headers: [],
    }
  },

  computed: {
    state () { return this.$store.state[`${this.itemType}s`] },
    items () {
      const items = this.state.available
      return Object.keys(items).map(id => {
        const item = items[`${id}`]
        return {
          id,
          name: id, // Hack to overcome vuetify's requirement of 'name' being defined, and unique
          itemName: item.name,
          code: item.code,
          selected: item.selected,
          current: id === this.state.current,
        }
      })
    },
    selected: {
      get: function () { return Object.values(this.items).filter(item => item.selected) },
      set: function (value) { this.$store.dispatch(`${this.itemType}s/select`, value) },
    }
  },

  mounted () {
    if (this.showName) {
      this.headers.push({
        text: this.headerName,
        align: 'left',
        sortable: false,
        value: 'itemName',
      })
    }
    if (this.showCode) {
      this.headers.push({
        text: 'Code',
        align: 'left',
        sortable: false,
        value: 'code',
      })
    }
  },

  methods: {
    current (id) {
      this.$store.dispatch(`${this.itemType}s/current`, {id})
    }
  }

}
</script>
