<template>
  <v-container>
    <v-table>
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
              <v-btn
                v-if="player?.in_server && player?.game?.id && player.game.id != game.id"
                class="ms-10"
                color="green"
                variant="outlined"
                @click="joinGame(game)"
                >Join
              </v-btn>
              <v-chip class="ms-10" color='green' v-else-if="player?.in_server && player?.game?.id && player.game.id == game.id">
                You Are In Game
              </v-chip>
              <copy-text
                class="ms-10"
                v-else
                :value="`/join ${game.id}`"
              ></copy-text>
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
  </v-container>
</template>

<script>
import CopyText from "../atom/CopyText.vue";
import GameWidget from "../widgets/GameWidget.vue";

export default {
  components: { GameWidget, CopyText },
  props: {
    games: Object,
    joinable: Boolean,
  },
  methods: {
    joinGame(game) {
      this.$api.joinGame(game);
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