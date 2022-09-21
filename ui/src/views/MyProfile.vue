<template>
  <v-container>
    <v-row class="d-flex flex-row">
      
      <!-- Player Stats -->
      <v-col md="8" lg="8" sm="12" cols="12">
        <v-card style="height:100%;">
          <v-card-title :style="{background: $vuetify.theme.themes.light.colors.background}">
            TBD
          </v-card-title>
          <v-card-content>
            Player Stats 
          </v-card-content>
        </v-card>
      </v-col>

      <!-- Player Card -->
      <v-col md="4" lg="4" sm="12" cols="12">
        <v-card style="height:100%;">
          <v-card-title class="justify-center" :style="{background: $vuetify.theme.themes.light.colors.background}" >
            <span>{{ player.username }}</span>
          </v-card-title>
          <v-card-content>
            <div class="d-flex justify-center mb-4">
              <img v-if="player.uuid" :src="`https://crafatar.com/renders/body/${player.uuid}`">
            </div>
            
            <h3>Owned Team {{ player?.owned_team?.full_name }}</h3>
            
            <invite-player-modal 
              class="mb-4"
              :style="{
                color: $vuetify.theme.themes.light.colors['on-primary'],
                background: $vuetify.theme.themes.light.colors.primary
              }" 
              block 
              @selected="e => sendInvite(e.player)"
            >
              Invite Players
            </invite-player-modal>

            <div v-if="player.isInTeam()">
              <h3>Member of</h3>
              <p>{{ player.team.short_name }}</p>
            </div>
            
          </v-card-content>
           
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Player } from '@/api/model/models'
import InvitePlayerModal from '@/components/modal/InvitePlayerModal.vue'
export default {
   components: { InvitePlayerModal },

    data () {
        return {
        }
    },

    computed: {
      player() {
        return this.$store.state.player
      },
      ownedTeam() {
        return this.$store.state.player?.owned_team
      }
    },

    async created() {
      let player_ids = await this.$api.getFFTPlayers();
      let players = player_ids.map(id => new Player(id));
      this.fftPlayers = players;
    },
}
</script>

<style>

</style>