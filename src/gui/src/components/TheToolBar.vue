<template>
  <v-toolbar>
    <v-toolbar-side-icon/>
    <v-toolbar-title>APS</v-toolbar-title>
    <v-spacer/>
    <v-btn
      icon
      @click="goBack"
    >
      <v-icon>apps</v-icon>
    </v-btn>
  </v-toolbar>
</template>

<script>
export default {
  methods: {
    goBack () {
      this.$router.push({name: 'GridModel'})
    }
  }
}
</script>
