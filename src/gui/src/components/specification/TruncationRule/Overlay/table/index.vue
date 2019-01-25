<template>
  <v-data-table
    :headers="headers"
    :items="groups"
    item-key="id"
    class="elevation-1"
    hide-actions
    @input.stop
  >
    <template
      slot="header-cell"
      slot-scope="props"
      class="text-xs-left"
    >
      <optional-help-item
        :value="props.header"
      />
    </template>
    <template
      slot="items"
      slot-scope="props"
    >
      <tr>
        <td>
          <background-facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <polygon-table
            v-if="props.item.polygons.length > 0"
            :value="props.item.polygons"
            :rule="value"
          />
          <span v-else>
            {{ 'Select one, or more background facies' }}
          </span>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script>
import BackgroundFaciesSpecification from '@/components/specification/Facies/background'
import OptionalHelpItem from '@/components/table/OptionalHelpItem'
import PolygonTable from './table'

import { AppTypes } from '@/utils/typing'
import { availableForBackgroundFacies } from '@/utils'

export default {
  name: 'BackgroundFacies',

  components: {
    OptionalHelpItem,
    BackgroundFaciesSpecification,
    PolygonTable,
  },

  props: {
    value: AppTypes.truncationRule.isRequired,
  },

  computed: {
    groups () {
      // TODO: Include 'help' messages
      let overlay = []
      if (this.value) {
        const groups = {}
        const polygons = this.value.overlayPolygons
        polygons.forEach(polygon => {
          if (!groups.hasOwnProperty(polygon.group)) groups[polygon.group] = []
          groups[polygon.group].push(polygon)
        })
        overlay = Object.keys(groups).map(groupId => { return { group: groupId, polygons: groups[`${groupId}`] } })
      }
      if (
        Object.values(this.$store.state.facies.available)
          .some(facies => availableForBackgroundFacies(this.$store.getters, this.value, facies)) &&
        this.value.overlayPolygons
          .map(({ group }) => this.$store.state.facies.groups.available[`${group}`])
          .every(group => group ? group.facies.length > 0 : true)
      ) {
        overlay.push({ group: '', polygons: [] })
      }
      return overlay
    },
    headers () {
      return [
        {
          text: 'Background',
          align: 'left',
          sortable: false,
          value: 'group',
          class: 'text-wrap-newline',
          help: 'Which facies this overlay polygon should cover',
        },
        {
          text: 'Polygons',
          align: 'left',
          sortable: false,
          value: 'polygon',
          help: 'Specification of the polygons',
        },
      ]
    }
  },

}
</script>
