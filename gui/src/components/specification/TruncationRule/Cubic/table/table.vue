<template>
  <base-table
    :headers="headers"
    :items="polygons"
    must-sort
  >
    <template
      v-slot:item="{ item }"
    >
      <tr>
        <td
          v-for="index in value.levels"
          :key="index"
        >
          {{ item.atLevel === index ? item.level.slice(0, index).join('.') : '' }}
        </td>
        <td>
          <background-facies-specification
            :value="item"
            :rule="value"
          />
        </td>
        <td
          v-if="hasMultipleFaciesSpecified"
        >
          <polygon-fraction-field
            :value="item"
            :rule="value"
          />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script lang="ts">
import BaseTable from '@/components/baseComponents/BaseTable.vue'
import { Component, Prop, Vue } from 'vue-property-decorator'

import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import BackgroundFaciesSpecification from '@/components/specification/Facies/background.vue'
import FractionField from '@/components/selection/FractionField.vue'
import PolygonFractionField from '@/components/selection/PolygonFractionField.vue'

import { sortByOrder } from '@/utils'
import { CubicPolygon } from '@/utils/domain'
import { hasFaciesSpecifiedForMultiplePolygons } from '@/utils/queries'
import { HeaderItems } from '@/utils/typing'

import Cubic from '@/utils/domain/truncationRule/cubic'

function makeLevelsHeader (levels: number): { text: string, value: string }[] {
  return [...new Array(levels)].map((_, index) => {
    return {
      text: `Level ${index + 1}`,
      value: 'level',
    }
  })
}

@Component({
  components: {
    BaseTable,
    BackgroundFaciesSpecification,
    FractionField,
    PolygonFractionField,
    OptionalHelpItem,
  },
})
export default class CubicFaciesSelection extends Vue {
  @Prop({ required: true })
  readonly value!: Cubic

  get headers (): HeaderItems {
    return [
      ...(makeLevelsHeader(this.value.levels)),
      {
        text: 'Facies',
        value: 'facies',
      },
      ...(this.hasMultipleFaciesSpecified
        ? [
          {
            text: 'Probability Fraction',
            value: 'fraction',
            help: 'The fraction of the facies probability assigned to the individual polygon',
          },
        ]
        : []),

    ]
  }

  get polygons (): CubicPolygon[] { return this.value.backgroundPolygons }

  get hasMultipleFaciesSpecified (): boolean {
    return hasFaciesSpecifiedForMultiplePolygons(this.polygons)
  }

  ordering (items: CubicPolygon[], index: number, isDescending: boolean): CubicPolygon[] { return sortByOrder(items, index, isDescending) }
}
</script>
