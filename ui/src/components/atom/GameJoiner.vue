<template>
  <v-btn
    v-if="player?.in_server && player?.game?.id != game.id"
    :color="game.isFull() ? 'red': 'green'"
    variant="outlined"
    :disabled="game.isFull()"
    @click="join()"
  >
    {{ game.isFull() ? "Game Full!" : "Join" }}
  </v-btn>
  <v-chip
    color="green"
    v-else-if="
      player?.in_server && player?.game?.id && player.game.id == game.id
    "
  >
    You Are In Game
  </v-chip>
  <div v-else>
    <copy-text v-if="!game.isFull()" :value="`/join ${game.id}`"></copy-text>
    <v-chip color="red" v-else>Game is Full</v-chip>
  </div>
</template>

<script>
import CopyText from "./CopyText.vue";
export default {
  components: { CopyText },
  props: {
    game: Object,
  },
  computed: {
    player() {
      return this.$store.state.player;
    },
  },
  methods: {
    join() {
      this.$api.joinGame(this.game);
    },
  },
};
</script>

<style>
</style>