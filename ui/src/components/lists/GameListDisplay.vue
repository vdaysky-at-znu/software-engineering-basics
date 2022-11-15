<template>
  <v-container>
    <v-table v-if="variant == 'table'">
      <thead>
        <tr>
          <th class="text-left">Map</th>
          <th class="text-right">Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="game in games" :key="game.id">
          <td class="d-flex align-center">
            <game-widget :game="game"></game-widget>

            <div v-if="joinable">
              <game-joiner :game="game"></game-joiner>
            </div>
          </td>

          <td class="text-end">
            <p v-if="game.is_finished">Finished</p>
            <p v-else-if="game.is_started">Live</p>
            <p v-else>Upcoming</p>
          </td>
        </tr>
      </tbody>
    </v-table>
    <v-row v-if="variant == 'cards'">
      <v-col v-for="game in games" :key="game.id">
        <game-card :game="game" :joinable="joinable"></game-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import GameCard from "@/components/cards/GameCard.vue";
import GameWidget from "../widgets/GameWidget.vue";
import GameJoiner from "../atom/GameJoiner.vue";

export default {
  components: { GameWidget, GameCard, GameJoiner },
  props: {
    games: Object,
    joinable: Boolean,
    variant: {
      type: String,
      default: "table",
    },
  },
  computed: {
    player() {
      return this.$store.state.player;
    },
  },
};
</script>

<style>
</style>