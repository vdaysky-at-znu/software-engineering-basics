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
        <contextual-list :source="players" :listComponent="PlayerList" propname="players" interactive paginated></contextual-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import PlayerList from '@/components/lists/PlayerList.vue'
import { Player } from '@/api/model/models'
import ContextualList from '@/components/contextual/ContextualList.vue'
export default {
  components: { ContextualList },
  setup() {
    return {
      PlayerList
    }
  },
  data() {
      return {
          players: Player.all(),
      }
  },
  created: function() {
  }
}
</script>

<style>

</style>