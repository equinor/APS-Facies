<template>
  <v-select
    :value="selected"
    :items="facies"
    multiple
    @input="e => update(e)"
  />
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator'

import { Facies } from '@/utils/domain'
import FaciesGroup from '@/utils/domain/facies/group'
import Polygon, { PolygonSerialization } from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import TruncationRule from '@/utils/domain/truncationRule/base'

function isFaciesSelected (group: FaciesGroup | undefined, facies: Facies): boolean {
  return group
    ? group.has(facies)
    : false
}

@Component
export default class BackgroundGroupFaciesSpecification<
  P extends Polygon = Polygon,
  S extends PolygonSerialization = PolygonSerialization,
> extends Vue {
  @Prop({ required: true })
  readonly value!: { group: ID, polygons: OverlayPolygon[]}

  @Prop({ required: true })
  readonly rule!: TruncationRule<P, S>

  get group (): FaciesGroup | undefined { return this.$store.state.facies.groups.available[`${this.value.group}`] }

  get selected () {
    return this.group
      ? this.group.facies
      : []
  }

  get facies () {
    return (Object.values(this.$store.state.facies.available) as Facies[])
      .filter(facies => facies.isChildOf(this.rule.parent))
      .map(facies => {
        return {
          value: facies,
          text: facies.alias,
          disabled: !isFaciesSelected(this.group, facies) /* I.e. the user should be allowed to DESELECT an already selected facies */
            && (!this.$store.getters['facies/availableForBackgroundFacies'](this.rule, facies)),
        }
      })
  }

  async update (facies: Facies[]) {
    if (!this.group) {
      const group = await this.$store.dispatch('facies/groups/add', { facies, parent: this.rule.parent })
      await this.$store.dispatch('truncationRules/addPolygon', { rule: this.rule, group, overlay: true })
    } else {
      await this.$store.dispatch('facies/groups/update', { group: this.group, facies })
    }
  }
}
</script>
