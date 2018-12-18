<template>
  <v-data-table
    v-model="selected"
    :headers="headers"
    :items="facies"
    must-sort
    item-key="name"
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
      <tr @click="() => current(props.item)">
        <td>
          <v-popover
            :disabled="canSelect"
            trigger="hover"
          >
            <v-checkbox
              v-model="props.selected"
              :indeterminate="props.item.selected === 'intermediate'"
              :disabled="!canSelect"
              primary
              hide-details
            />
            <span slot="popover">
              {{ selectFaciesError }}
            </span>
          </v-popover>
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
import { mapState, mapGetters } from 'vuex'
import Swatches from 'vue-swatches'
import VueTypes from 'vue-types'

import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import { hasCurrentParents } from '@/utils'

export default {
  components: {
    OptionalHelpItem,
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
          sortable: true,
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
    ...mapGetters({
      'canSelect': 'canSpecifyModelSettings',
    }),
    ...mapState({
      facies: state => Object.values(state.facies.global.available)
        .map(facies => {
          return {
            id: facies.id,
            ...facies,
            current: facies.id === state.facies.global.current,
          }
        }),
      parent: state => { return { zone: state.zones.current, region: state.regions.current } },
    }),
    selected: {
      get: function () {
        const state = this.$store.state
        const getters = this.$store.getters
        return Object.values(state.facies.global.available)
          .filter(facies => Object.values(state.facies.available)
            .filter(facies => hasCurrentParents(facies, getters))
            .findIndex(localFacies => localFacies.facies === facies.id) >= 0)
      },
      set: function (value) {
        this.$store.dispatch('facies/select', { items: value, parent: this.parent })
      },
    },
    availableColors () {
      return this.$store.state.constants.faciesColors.available
    },
    selectFaciesError () {
      const item = this.$store.state.regions.use && !this.parent.region
        ? 'Region'
        : 'Zone'
      return !this.canSelect
        ? `A ${item} must be selected, before including a facies in the model`
        : ''
    },
  },

  methods: {
    changeColor (facies, color) {
      if (facies.color !== color) {
        // Only dispatch when the color *actually* changes
        return this.$store.dispatch('facies/global/changed', { id: facies.id, color })
      } else {
        return Promise.resolve(facies)
      }
    },
    current ({ id }) {
      return this.$store.dispatch('facies/global/current', { id })
    },
    changeName (value) {
      return this.$store.dispatch('facies/global/changed', { id: value.id, name: value.name || `F${value.code}` })
    },
    changeAlias (facies) {
      return this.$store.dispatch('facies/global/changed', { id: facies.id, alias: facies.alias })
    },
  },

}
</script>
