<template>
  <v-container>
    <v-row class="d-flex flex-row">
      
      <!-- Player Stats -->
      <v-col md="8" lg="8" sm="12" cols="12">
        <v-card style="height:100%;">
          <v-card-title :style="{background: $vuetify.theme.themes.light.colors.background}">
            Stats
          </v-card-title>
          <v-card-content>
            
            <div class="d-flex justify-space-between pb-5">
              <stat-badge>
                <template v-slot:metric>
                  Ranked Elo
                </template>
                <template v-slot:value>
                  {{ player.elo }}
                </template>
              </stat-badge>

              <stat-badge>
                <template v-slot:metric>
                  Total Games Played
                </template>
                <template v-slot:value>
                  {{ stat?.games_played }}
                </template>
              </stat-badge>

              <stat-badge>
                <template v-slot:metric>
                  Total Wins
                </template>
                <template v-slot:value>
                  {{ stat?.games_won }}
                </template>
              </stat-badge>

              <stat-badge>
                <template v-slot:metric>
                  Ranked Games
                </template>
                <template v-slot:value>
                  {{ stat?.ranked_games_played }}
                </template>
              </stat-badge>

              <stat-badge>
                <template v-slot:metric>
                  Ranked Wins
                </template>
                <template v-slot:value>
                  {{ stat?.ranked_games_won }}
                </template>
              </stat-badge>
            </div>
            
            <v-table>
              <thead>
                <tr>
                  <th class="text-center">Kills</th>
                  <th class="text-center">Deaths</th>
                  <th class="text-center">Assists</th>
                  <th class="text-center">K/D</th>
                  <th class="text-center">HS%</th>
                </tr>
              </thead>
              <tbody>
                <tr class="text-center">
                  <td>{{ stat?.kills }}</td>
                  <td>{{ stat?.deaths }}</td>
                  <td>{{ stat?.assists }}</td>
                  <td>{{ stat?.kd?.() }}</td>
                  <td>{{ stat?.hs }}</td>
                </tr>
              </tbody>
            </v-table>

            <v-card >
              <v-card-title>
                TBD
              </v-card-title>
              <v-card-content>
                TBD
              </v-card-content>
            </v-card>

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
            <div class="d-flex justify-center mb-4 py-3" style="background: #e7e7e7; box-shadow: #e7e7e7 0px 0px 7px 2px;">
              <img v-if="player.uuid" :src="`https://crafatar.com/renders/body/${player.uuid}`">
            </div>
            
            <v-divider class="my-4"></v-divider>
            
            <div v-if="player.owned_team" class="text-center">
              <span> Team Owner </span>
              <team-widget :team="player.owned_team"></team-widget>

              <invite-player-modal 
                v-if="own"
                class="my-4"
                :style="{
                  color: $vuetify.theme.themes.light.colors['on-primary'],
                  background: $vuetify.theme.themes.light.colors.primary
                }" 
                block 
                @selected="e => sendInvite(e.player)"
              >
                Invite Players
              </invite-player-modal>

              <v-divider class="my-4"></v-divider>

            </div>

            <div class="d-flex" v-if="player.isInTeam()">
              <h3 class="me-3">Member of</h3>
              <team-widget :team="player.team"></team-widget>
            </div>

            <v-btn v-if="own" block color="error">Log Out</v-btn>

            
          </v-card-content>
           
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import InvitePlayerModal from '@/components/modal/InvitePlayerModal.vue'
import TeamWidget from '@/components/widgets/TeamWidget.vue'
import { PlayerExtendedPerformanceAggregatedView } from '@/api/model/models'
import StatBadge from '../atom/StatBadge.vue'
export default {
   components: { InvitePlayerModal, TeamWidget, StatBadge },

    props: ['player', 'own'],

    data () {
        return {
          stat: null,
        }
    },

    watch: {
      player_id: {
        immediate: true,
        handler(newVal) {
        
          if (newVal) {
            this.stat = new PlayerExtendedPerformanceAggregatedView({player_id: newVal})
          }
        },
      }
    },

    computed: {
      ownedTeam() {
        return this.player?.owned_team
      },
      player_id() {
        return this.player?.id
      }
    },
}
</script>

<style>

</style>