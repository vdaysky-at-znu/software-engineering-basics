<template>
  <v-container>
    <game-list :games="deathmatch.games" variant="cards" paginated interactive>
    </game-list>
  </v-container>
</template>

<script>
import { DeathMatchView } from '@/api/model/models'
import GameList from '@/components/contextual/GameList.vue'
export default {
  components: { GameList },
  data() {
    return {
      deathmatch: new DeathMatchView({})
    }
  },
}
</script>

<style>

</style>