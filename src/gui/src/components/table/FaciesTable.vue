<template>
  <v-data-table
    :headers="headers"
    :items="facies"
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
import HighlightCurrentItem from '@/components/baseComponents/HighlightCurrentItem'

export default {
  components: {
    HighlightCurrentItem,
    Swatches,
  },

  props: {
  },

  data () {
    return {
      headers: [
        {
          text: 'Facies',
          align: 'left',
          sortable: false,
          value: 'name',
        },
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
            name: facies.name,
            code: facies.code,
            color: facies.color,
            current: id === state.facies.current,
          }
        }),
    }),
    availableColors () {
      return this.$store.state.constants.faciesColors.available
    },
  },

  methods: {
    changeColor (facies, color) {
      if (facies.color !== color) {
        // Only dispatch when the color *actually* changes
        return this.$store.dispatch('facies/changed', {
          facies: {
            id: facies.id,
            code: facies.code,
            name: facies.name,
            color,
          }
        })
      } else {
        return Promise.resolve(facies)
      }
    },
    current ({ id }) {
      this.$store.dispatch('facies/current', { id })
    },
    changeName (value) {
      const facies = {
        id: value.id,
        name: value.name,
        code: value.code,
        color: value.color,
      }
      if (facies.name === '') {
        facies.name = `F${value.code}`
      }
      return this.$store.dispatch('facies/changed', { facies })
    },
  },

}
</script>
