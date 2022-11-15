<template>
  <v-container class="">
    <v-row>
      <v-col>
        <game-mode min-height="100%"
          name="Pub"
          description="Play classic defusal MineStrike without risking your rating"
          :online="stats.pubs_online"
          :lobbies="stats.pubs_games"
          @selected="$router.push({ name: 'pubs' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="RankedMS"
          description="Defusal Mode with a rating system"
          :online="stats.ranked_online"
          :lobbies="stats.ranked_games"
          @selected="$router.push({ name: 'ranked' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="Deathmatch"
          description="Deathmatch mode. Instant respwans, free weapons. Get as many kills as you can"
          :online="stats.deathmatch_online"
          :lobbies="stats.deathmatch_games"
          @selected="$router.push({ name: 'deathmatch' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="Duels"
          description="1v1 duels. No rating system"
          :online="stats.duels_online"
          :lobbies="stats.duels_games"
          @selected="$router.push({ name: 'duels' })"
        ></game-mode>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GameMode from "@/components/modules/play/GameMode.vue";
import { GameModeStatsView } from "@/api/model/models"; 
export default {
  components: { GameMode },
  data() {
    return {
      stats: null
    };
  },
  created() {
    this.stats = new GameModeStatsView({});
  }
};
</script>

<style>
</style>