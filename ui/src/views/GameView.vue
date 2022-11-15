<template>
  <v-container>
    <h1 class="text-center">{{ game?.map?.display_name }}</h1>

    <div v-if="game.match" class="text-center">
      <match-widget :match="game.match"></match-widget>
    </div>
    
    <v-container class="pb-0">
      <h2>
        {{ game.team_a?.name || sideName(game?.team_a?.is_ct) }} - {{ game.score_a }}
      </h2>
    </v-container>
    
    <team-score :team="game.team_a"></team-score>

    <v-container class="pb-0">
      <h2>
        {{ game.team_b?.name || sideName(game?.team_b?.is_ct) }} - {{ game.score_b }}
      </h2>
    </v-container>
    
    <team-score :team="game.team_b"></team-score>
  </v-container>
</template>

<script>
import TeamScore from '@/components/subview/TeamScore.vue'
import { Game } from '@/api/model/models'
import MatchWidget from '@/components/widgets/MatchWidget.vue'
export default {
  components: { TeamScore, MatchWidget },
  data(){
    return {
      game: new Game(this.$route.params.id),
    }
  },
  methods: {
    sideName(isCT) {
      return isCT ? 'SWAT' : 'Terrorists'
    }
  }

}
</script>

<style>

</style>