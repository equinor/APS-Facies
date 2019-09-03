<template>
  <base-table
    :headers="headers"
    :items="polygons"
    @input.stop
  >
    <template
      v-slot:item="{ item }"
    >
      <tr>
        <td class="text-left">
          <optional-help-item
            :value="item.name"
          />
        </td>
        <td class="text-left">
          <!--TODO: Figure out why input happens twice-->
          <facies-specification
            :value="item"
            :rule="value"
          />
        </td>
        <td>
          <fraction-field
            v-if="!!item.slantFactor"
            :value="item.slantFactor"
            fmu-updatable
            @input="factor => updateFactor(item, factor)"
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

  get polygons () {
    return !this.value
      ? []
      : this.value.backgroundPolygons
  }

  get headers () {
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

  async updateFactor (item: BayfillPolygon, value: number) {
    await this.$store.dispatch('truncationRules/changeSlantFactors', {
      rule: this.value,
      polygon: item,
      value
    })
  }
}
</script>
