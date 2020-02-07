<template>
  <base-table
    :headers="headers"
    :items="polygons"
    @input.stop
  >
    <template
      v-slot:item="{ item : polygon }"
    >
      <tr>
        <td class="text-left">
          <optional-help-item
            :value="polygon.name"
          />
        </td>
        <td class="text-left">
          <!--TODO: Figure out why input happens twice-->
          <facies-specification
            :value="polygon"
            :rule="value"
            clearable
          />
        </td>
        <td>
          <fraction-field
            v-if="!!polygon.slantFactor"
            :value="polygon.slantFactor"
            fmu-updatable
            @input="factor => updateFactor(polygon, factor)"
          />
          <slot v-else />
        </td>
      </tr>
    </template>
  </base-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import FaciesSpecification from '@/components/specification/Facies/index.vue'
import BaseTable from '@/components/baseComponents/BaseTable.vue'

import { Bayfill, BayfillPolygon } from '@/utils/domain'
import { HeaderItems } from '@/utils/typing'

@Component({
  components: {
    BaseTable,
    OptionalHelpItem,
    FractionField,
    FaciesSpecification,
  },
})
export default class BayfillPolygonTable extends Vue {
  @Prop({ required: true })
  readonly value!: Bayfill

  get polygons (): BayfillPolygon[] {
    return !this.value
      ? []
      : this.value.backgroundPolygons
  }

  get headers (): HeaderItems {
    return [
      {
        text: 'Polygon',
        value: 'name',
      },
      {
        text: 'Facies',
        value: 'facies',
      },
      {
        text: 'Slant Factor',
        value: 'factor',
      }
    ]
  }

  async updateFactor (item: BayfillPolygon, value: number): Promise<void> {
    await this.$store.dispatch('truncationRules/changeSlantFactors', {
      rule: this.value,
      polygon: item,
      value
    })
  }
}
</script>
