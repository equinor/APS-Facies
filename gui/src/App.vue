<template>
  <v-app id="app">
    <v-app-bar flat color="#ffffff">
      <v-col class="column">
        <the-tool-bar />
      </v-col>
    </v-app-bar>
    <v-main>
    <the-information-bar />
      <main-page />
    </v-main>
  </v-app>
</template>

<script lang="ts" setup>
import TheToolBar from '@/components/TheToolBar.vue'
import TheInformationBar from '@/components/TheInformationBar.vue'
import MainPage from '@/pages/MainPage.vue'
import { onBeforeMount } from 'vue'
import { useStore } from './store'

const store = useStore()

onBeforeMount(() => {
  if (!store.getters.loaded && !store.getters.loading) {
    // Fetch various parameters
    store.dispatch('fetch')
  }
})
</script>

<style lang="scss" scoped>
@import 'style/main';

#app {
  font-family: $font-family;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1,
h2 {
  font-weight: normal;
}

ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 0;
}
</style>
