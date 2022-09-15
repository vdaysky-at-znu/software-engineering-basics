<template>
  <v-container>
      <v-row v-for="(team, i) in teams" :key="i">
            <v-col cols="12" sm="6" md="4" lg="3" xl="2" :key="i">
                <team-widget :team="team"></team-widget>
            </v-col>
      </v-row>
  </v-container>
</template>

<script>
import TeamWidget from '../widgets/TeamWidget.vue'
export default {
    props: ['teams'],
    components: {
        TeamWidget
    }
}
</script>

<style>

</style>