<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
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
      <td
        v-for="index in value.levels"
        :key="index"
      >
        {{ props.item.atLevel === index ? props.item.level.slice(0, index).join('.') : '' }}
      </td>
      <td>
        <background-facies-specification
          :value="props.item"
          :rule="value"
        />
      </td>
      <td
        v-if="hasMultipleFaciesSpecified"
      >
        <polygon-fraction-field
          :value="props.item"
          :rule="value"
        />
      </td>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import BackgroundFaciesSpecification from '@/components/specification/Facies/background.vue'
import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'

import { sortByOrder } from '@/utils'
import { CubicPolygon, Facies } from '@/utils/domain'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'

import Cubic from '@/utils/domain/truncationRule/cubic'

function makeLevelsHeader (levels: number) {
  return [...new Array(levels)].map((_, index) => {
    return {
      text: `Level ${index + 1}`,
      align: 'left',
      sortable: false,
      value: 'level',
    }
  })
}

@Component({
  components: {
    BackgroundFaciesSpecification,
    FractionField,
    PolygonFractionField,
    OptionalHelpItem,
  },
})
export default class CubicFaciesSelection extends Vue {
  @Prop({ required: true })
  readonly value!: Cubic

  get headers () {
    return [
      ...(makeLevelsHeader(this.value.levels)),
      {
        text: 'Facies',
        align: 'left',
        sortable: false,
        value: 'facies',
      },
      ...(this.hasMultipleFaciesSpecified ? [
        {
          text: 'Probability Fraction',
          align: 'left',
          sortable: false,
          value: 'fraction',
          help: 'The fraction of the facies probability assigned to the individual polygon',
        },
      ] : []),

    ]
  }

  get polygons () { return this.value.backgroundPolygons }

  get hasMultipleFaciesSpecified () {
    return hasFaciesSpecifiedForMultiplePolygons(this.polygons)
  }

  multipleFaciesSpecified ({ facies }: Facies) {
    return hasFaciesSpecifiedForMultiplePolygons(this.value.polygons, facies)
  }

  ordering (items: CubicPolygon[], index: number, isDescending: boolean) { return sortByOrder(items, index, isDescending) }
}
</script>
