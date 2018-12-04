<template>
  <v-container>
    <v-data-table
      :headers="headers"
      :items="items"
      v-model="selectedItems"
      :item-key="itemKey"
      :class="tableClass"
      hide-actions
      @input="inputChanged"
    >
      <template
        slot="items"
        slot-scope="props"
      >
        <td class="text-xs-left">{{ props.item.name }}</td>
      </template>
    </v-data-table>
  </v-container>
</template>

<script>
import VueTypes from 'vue-types'
import { AppTypes } from '@/utils/typing'

export default {
  props: {
    items: VueTypes.arrayOf(VueTypes.shape({
      name: AppTypes.name,
      selected: VueTypes.bool
    }).loose).isRequired,

    headers: VueTypes.arrayOf(VueTypes.shape({
      text: VueTypes.string.isRequired,
      value: VueTypes.string.isRequired,
      align: VueTypes.oneOf(['left', 'center', 'right']),
      sortable: VueTypes.bool.def(true),
      class: VueTypes.oneOfType([VueTypes.arrayOf(VueTypes.string), VueTypes.string]),
      width: VueTypes.string
    })).isRequired,

    itemKey: VueTypes.string.def('name'),

    tableClass: VueTypes.string.def('elevation-1')
  },

  data () {
    return {
      selectedItems: [],
      selectedRow: null
    }
  },

  methods: {
    inputChanged (value) {
      const selectedItems = value.map(item => item.name)
      this.$emit('selected', selectedItems)
    },

    defaults () {
      return {
        key: 'name',
        class: 'elevation-1',
        sortable: true
      }
    }
  }
}
</script>
