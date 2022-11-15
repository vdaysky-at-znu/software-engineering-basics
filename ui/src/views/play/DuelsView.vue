<template>
  <v-container>
    <game-list :games="duels.games" variant="cards" paginated interactive>
    </game-list>
  </v-container>
</template>

<script>
import { DuelsView } from "@/api/model/models";
import GameList from "@/components/contextual/GameList.vue";
export default {
  components: { GameList },
  data() {
    return {
      duels: new DuelsView({}),
    }
  },
};
</script>

<style>
</style>