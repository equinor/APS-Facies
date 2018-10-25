<template>
  <v-data-table
    :headers="headers"
    :items="facies"
    v-model="selected"
    item-key="name"
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
      <tr @click="() => current(props.item)">
        <td>
          <v-checkbox
            v-model="props.selected"
            :indeterminate="props.item.selected === 'intermediate'"
            primary
            hide-details
          />
        </td>
        <td class="text-xs-left">
          <v-edit-dialog
            lazy
          >
            <highlight-current-item
              :item="props.item"
              field="name"
            />
            <v-text-field
              slot="input"
              v-model="props.item.name"
              label="Edit"
              single-line
              @keydown.enter="() => changeName(props.item)"
            />
          </v-edit-dialog>
        </td>
        <td
          v-if="!hideAlias"
          class="text-xs-left"
        >
          <v-edit-dialog
            lazy
          >
            <highlight-current-item
              :item="props.item"
              field="alias"
            />
            <v-text-field
              slot="input"
              v-model="props.item.alias"
              label="Edit"
              single-line
              @keydown.enter="() => changeAlias(props.item)"
            />
          </v-edit-dialog>
        </td>
        <td class="text-xs-left">
          <highlight-current-item
            :item="props.item"
            field="code"
          />
        </td>
        <td
          :style="{backgroundColor: props.item.color}"
          @click.stop="props.expanded = !props.expanded"
        />
      </tr>
    </template>
    <template
      slot="expand"
      slot-scope="props"
    >
      <swatches
        :value="props.item.color"
        :colors="availableColors"
        inline
        popover-to="left"
        swatches-size="30"
        @input="color => changeColor(props.item, color)"
      />
    </template>
  </v-data-table>
</template>

<script>
import { mapState } from 'vuex'
import Swatches from 'vue-swatches'
import VueTypes from 'vue-types'

import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem'

export default {
  components: {
    HighlightCurrentItem,
    Swatches,
  },

  props: {
    hideAlias: VueTypes.bool.def(false),
  },

  data () {
    return {
      headers: [
        {
          text: 'Use',
          align: 'left',
          sortable: false,
          value: 'selected',
        },
        {
          text: 'Facies',
          align: 'left',
          sortable: false,
          value: 'name',
        },
        ...(this.hideAlias ? [] : [
          {
            text: 'Alias',
            align: 'left',
            sortable: false,
            value: 'alias'
          },
        ]),
        {
          text: 'Code',
          align: 'left',
          sortable: false,
          value: 'code',
        },
        {
          text: 'Color',
          align: 'left',
          sortable: false,
          value: 'color',
        }
      ],
    }
  },

  computed: {
    ...mapState({
      facies: state => Object.keys(state.facies.available)
        .map(id => {
          const facies = state.facies.available[`${id}`]
          return {
            id,
            ...facies,
            current: id === state.facies.current,
          }
        }),
    }),
    selected: {
      get: function () { return Object.values(this.facies).filter(item => item.selected) },
      set: function (value) { this.$store.dispatch('facies/select', value) },
    },
    availableColors () {
      return this.$store.state.constants.faciesColors.available
    },
  },

  methods: {
    changeColor (facies, color) {
      if (facies.color !== color) {
        // Only dispatch when the color *actually* changes
        return this.$store.dispatch('facies/changed', { id: facies.id, color })
      } else {
        return Promise.resolve(facies)
      }
    },
    current ({ id }) {
      return this.$store.dispatch('facies/current', { id })
    },
    changeName (value) {
      return this.$store.dispatch('facies/changed', { id: value.id, name: value.name || `F${value.code}` })
    },
    changeAlias (facies) {
      return this.$store.dispatch('facies/changed', { id: facies.id, alias: facies.alias })
    },
  },

}
</script>
