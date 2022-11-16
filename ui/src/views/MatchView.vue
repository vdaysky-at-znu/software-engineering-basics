<template>
  <v-container>
    <v-row>
      <v-col>
        <h1 class="text-center">
          {{ match.name }}
        </h1>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-if="!mdAndDown" lg="3">
        <team-sub-view hideTeam v-if="match?.team_one" :team="match.team_one"></team-sub-view>
      </v-col>
      <v-col lg="6">
        <map-pick-process-view v-if="match?.map_pick_process" :mapPickProcess="match.map_pick_process"></map-pick-process-view>
      </v-col>
      <v-col v-if="!mdAndDown" lg="3">
        <team-sub-view hideTeam v-if="match?.team_two" :team="match.team_two"></team-sub-view>
      </v-col>
    </v-row>
    
    <v-row class="justify-center">
      <v-col cols="12" lg="6">
        <h3 class="text-center">Games</h3>
        <game-list :games="match.games"></game-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Match } from '@/api/model/models'
import MapPickProcessView from './MapPickProcessView.vue'
import TeamSubView from '@/components/subview/TeamSubView.vue'
import GameList from '@/components/lists/GameList.vue'
import { useDisplay } from 'vuetify/lib/framework.mjs'

export default {
  components: { MapPickProcessView, TeamSubView, GameList },
  setup() {
    const { xs, smAndUp, smAndDown, mdAndDown } = useDisplay();
    return {
      GameList, xs, smAndUp, smAndDown, mdAndDown
    }
  },

  data: function(){
      return { 
        match: new Match(this.$route.params.id),
      }
  },
}
</script>

<style>

</style>