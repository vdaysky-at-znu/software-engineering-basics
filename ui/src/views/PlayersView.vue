<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Players</h1>
        <code> {{ players.count }} players found </code>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <player-list :players="players" interactive paginated>
        </player-list>
        
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Player } from "@/api/model/models";
import PlayerList from '@/components/lists/PlayerList.vue';
export default {
  components: { PlayerList },
  setup() {
    return {
      PlayerList,
    };
  },
  data() {
    return {
      players: Player.all(),
    };
  },
  created: function () {},
};
</script>

<style>
</style>