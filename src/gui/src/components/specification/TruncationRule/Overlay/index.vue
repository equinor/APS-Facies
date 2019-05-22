<template>
  <v-layout
    column
  >
    <v-layout
      align-center
      justify-space-between
      row
      fill-height
    >
      <h3>Overlay Facies</h3>
    </v-layout>
    <overlay-facies-table
      :value="value"
    />
  </v-layout>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import OverlayFaciesTable from './table/index.vue'

import Polygon, { PolygonSpecification } from '@/utils/domain/polygon/base'
import OverlayTruncationRule from '@/utils/domain/truncationRule/overlay'

@Component({
  components: {
    OverlayFaciesTable,
  },
})
export default class OverlaySpecification<T extends Polygon, P extends PolygonSpecification> extends Vue {
  @Prop({ required: true })
  readonly value!: OverlayTruncationRule<T, P>
}
</script>
