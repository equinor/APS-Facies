<template>
  <h2><slot /></h2>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator'

@Component
export default class SectionTitle extends Vue {
}
</script>
