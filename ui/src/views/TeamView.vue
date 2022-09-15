<template>
  <v-container>
      <team-widget :team="team"></team-widget>
  </v-container>
</template>

<script>
import TeamWidget from "@/components/widgets/TeamWidget.vue"
import { Team } from '@/api/model/models'

export default {
    components: { TeamWidget },
    data() {
        return {
            team: new Team(this.$route.params.team),
        }
    },
}
</script>

<style>

</style>