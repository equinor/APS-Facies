<template>
  <v-data-table
    :headers="headers"
    :items="polygons"
    item-key="name"
    class="elevation-1"
    hide-actions
    @input.stop
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
      <tr>
        <td class="text-xs-left">
          <optional-help-item
            :value="props.item.name"
          />
        </td>
        <td class="text-xs-left">
          <!--TODO: Figure out why input happens twice-->
          <facies-specification
            :value="props.item"
            :rule="value"
          />
        </td>
        <td>
          <fraction-field
            v-if="!!props.item.slantFactor"
            :value="props.item.slantFactor"
            fmu-updatable
            @input="factor => updateFactor(props.item, factor)"
          />
          <slot v-else />
        </td>
      </tr>
    </template>
  </v-data-table>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import FractionField from '@/components/selection/FractionField.vue'
import OptionalHelpItem from '@/components/table/OptionalHelpItem.vue'
import FaciesSpecification from '@/components/specification/Facies/index.vue'

import { Bayfill, BayfillPolygon } from '@/utils/domain'

@Component({
  components: {
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
        align: 'left',
        sortable: false,
        value: 'name',
        help: '',
      },
      {
        text: 'Facies',
        align: 'left',
        sortable: false,
        value: 'facies',
        help: '',
      },
      {
        text: 'Slant Factor',
        align: 'left',
        sortable: false,
        value: 'factor',
        help: '',
      }
    ]
  }

  async updateFactor (item: BayfillPolygon, value: number) {
    return this.$store.dispatch('truncationRules/changeSlantFactors', {
      rule: this.value,
      polygon: item,
      value
    })
  }
}
</script>
