<template>
  <v-container>
    <v-container class="pb-0">
      <h2>
        {{ game.team_a?.name }} - {{ game.score_a }}
      </h2>
    </v-container>
    
    <team-score :team="game.team_a"></team-score>

    <v-container class="pb-0">
      <h2>
        {{ game.team_b?.name }} - {{ game.score_b }}
      </h2>
    </v-container>
    
    <team-score :team="game.team_b"></team-score>
  </v-container>
</template>

<script>
import TeamScore from '@/components/subview/TeamScore.vue'
import { Game } from '@/api/model/models'
export default {
  components: { TeamScore },
  data(){
    return {
      game: new Game(this.$route.params.id),
    }
  },

}
</script>

<style>

</style>