<template>
  <v-select
    :value="selected"
    :items="facies"
    multiple
    @input="e => update(e)"
  />
</template>

<script>
import VueTypes from 'vue-types'

import { AppTypes } from '@/utils/typing'
import { availableForBackgroundFacies } from '@/utils'

const isFaciesSelected = (group, facies) => {
  return group
    ? group.has(facies)
    : false
}

export default {
  name: 'BackgroundFaciesSpecification',

  components: {
  },

  props: {
    rule: AppTypes.truncationRule.isRequired,
    value: VueTypes.shape({
      group: AppTypes.id.isRequired,
    }).loose.isRequired,
  },

  computed: {
    group () { return this.$store.state.facies.groups.available[`${this.value.group}`] },
    selected () {
      const group = this.$store.getters['facies/byId'](this.value.group)
      if (group) {
        return group.map(({ id }) => id)
      } else {
        return []
      }
    },
    facies () {
      return Object.values(this.$store.state.facies.available)
        .map(facies => {
          return {
            value: facies.id,
            text: this.$store.getters['facies/name'](facies),
            disabled: !isFaciesSelected(this.group, facies) /* I.e. the user should be allowed to DESELECT an already selected facies */ && (
              !availableForBackgroundFacies(this.$store.getters, this.rule, facies)
            ),
          }
        })
    },
  },

  methods: {
    async update (facies) {
      if (!this.group) {
        const group = await this.$store.dispatch('facies/groups/add', { facies, ...this.rule.parent })
        await this.$store.dispatch('truncationRules/addPolygon', { rule: this.rule, group, overlay: true })
      } else {
        await this.$store.dispatch('facies/groups/update', { group: this.group, facies })
      }
    },
  },
}
</script>
