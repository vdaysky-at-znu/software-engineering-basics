<template>
  <v-container class="">
    <v-row>
      <v-col>
        <game-mode min-height="100%"
          name="Pub"
          description="Play classic defusal MineStrike without risking your rating"
          :online="69"
          :lobbies="420"
          @selected="$router.push({ name: 'pubs' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="RankedMS"
          description="Defusal Mode with a rating system"
          :online="69"
          :lobbies="420"
          @selected="$router.push({ name: 'ranked' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="Deathmatch"
          description="Deathmatch mode. Instant respwans, free weapons. Get as many kills as you can"
          :online="69"
          :lobbies="420"
          @selected="$router.push({ name: 'deathmatch' })"
        ></game-mode>
      </v-col>
      <v-col>
        <game-mode min-height="100%"
          name="Duels"
          description="1v1 duels. No rating system"
          :online="69"
          :lobbies="420"
          @selected="$router.push({ name: 'duels' })"
        ></game-mode>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GameMode from "@/components/modules/play/GameMode.vue";
export default {
  components: { GameMode },
};
</script>

<style>
</style>