<template>
  <div class="d-flex">
    <v-chip color="green" v-if="player.in_server">Online</v-chip>
    <router-link :to="{ name: 'profile' }">
      <div class="d-flex align-center">
        <span class="pe-2">
          {{ player.username }}
        </span>
        <player-avatar :player="player"></player-avatar>
      </div>
    </router-link>
  </div>
</template>

<script>
import playerAvatar from "./atom/player-avatar.vue";
export default {
  components: { playerAvatar },
  data: () => ({}),
  computed: {
    player() {
      return this.$store.state.player;
    },
  },
};
</script>

<style>
</style>