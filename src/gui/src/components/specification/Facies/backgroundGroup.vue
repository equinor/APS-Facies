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
import { RootGetters } from '@/store/typing'
import FaciesGroup from '@/utils/domain/facies/group'
import Polygon from '@/utils/domain/polygon/base'
import { ID } from '@/utils/domain/types'
import OverlayPolygon from '@/utils/domain/polygon/overlay'
import TruncationRule from '@/utils/domain/truncationRule/base'

function isFaciesSelected (group: FaciesGroup | undefined, facies: Facies): boolean {
  return group
    ? group.has(facies)
    : false
}

@Component
export default class BackgroundGroupFaciesSpecification<P extends Polygon> extends Vue {
  @Prop({ required: true })
  readonly value!: { group: ID, polygons: OverlayPolygon[]}

  @Prop({ required: true })
  readonly rule!: TruncationRule<P>

  get group (): FaciesGroup | undefined { return this.$store.state.facies.groups.available[`${this.value.group}`] }

  get selected () {
    return this.group
      ? this.group.facies.map(({ id }) => id)
      : []
  }

  get facies () {
    return (Object.values(this.$store.state.facies.available) as Facies[])
      .map(facies => {
        return {
          value: facies.id,
          text: facies.name,
          disabled: !isFaciesSelected(this.group, facies) /* I.e. the user should be allowed to DESELECT an already selected facies */
            && (!this.$store.getters['facies/availableForBackgroundFacies'](this.rule, facies)),
        }
      })
  }

  async update (ids: ID[]) {
    const facies = ids.map(id => (this.$store.getters as RootGetters)['facies/byId'](id))
    if (!this.group) {
      const group = await this.$store.dispatch('facies/groups/add', { facies, ...this.rule.parent })
      await this.$store.dispatch('truncationRules/addPolygon', { rule: this.rule, group, overlay: true })
    } else {
      await this.$store.dispatch('facies/groups/update', { group: this.group, facies })
    }
  }
}
</script>
