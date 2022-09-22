<template>
  <v-container>
      <player-list :players="players"></player-list>
  </v-container>
</template>

<script>
import PlayerList from '@/components/lists/PlayerList.vue'
import { Player } from '@/api/model/models'
export default {
  components: { PlayerList },
  data() {
      return {
          players: Player.all(),
      }
  },
}
</script>

<style>

</style>