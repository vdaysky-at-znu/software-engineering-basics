<template>
  <v-container>
    <v-card>
      <v-card-title class="justify-center">
        <span>{{ title }}</span>
      </v-card-title>
      <v-card-text class="pt-0">
        <player-list
          :players="players"
          :exclude="['team', 'elo', 'index']"
        >
        </player-list>

      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import PlayerList from "@/components/lists/PlayerList.vue";
import { MatchTeam } from '@/api/model/models';
export default {
    components: { PlayerList },
    props: {'team': null},
    computed: {
      isMatchTeam() {
        return this.team instanceof MatchTeam;
      },
      title() {
        if (this.isMatchTeam) {
          return this.team.name;
        }
        return this.team.short_name + " | " + this.team.elo + " Elo"; 
      },
      players() {
        if (this.isMatchTeam) {
          return this.team.players;
        }
        return this.team.members;
      },
    },
    created() {
      console.log("TeamSubView created");
    }

}
</script>

<style>

</style>