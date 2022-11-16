<template>
  <player-profile :player="player" :own="false"></player-profile>
</template>

<script>
import { Player } from "@/api/model/models.js";
import PlayerProfile from "@/components/common/PlayerProfile.vue";

export default {
  components: { PlayerProfile },
  computed: {
    playerId() {
      return this.$route.params.id;
    },
    player() {
      return new Player(this.playerId);
    },
  },
};
</script>

<style>
</style>