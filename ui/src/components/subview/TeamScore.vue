<template>
  <v-container>
    <v-table>
        <thead>
            <tr>
                <th>
                    #
                </th>
                <th>
                    Player
                </th>
                <th>
                    Kills
                </th>
                <th>
                    Deaths
                </th>
                <th>
                    Assists
                </th>

                <th>
                    K/D
                </th>

                <th>
                    HS%
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(stat, i) in statsView?.stats" :key="stat">
                <td width="8%">
                    {{ i + 1 }}.
                </td>
                <td>
                    <player-widget v-if="stat.player" :player="stat.player"></player-widget>
                </td>
                <td>
                    {{ stat.kills }}
                </td>
                <td>
                    {{ stat.deaths }}
                </td>
                <td>
                    {{ stat.assists }}
                </td>
                <td>
                    {{ stat.kd() }}
                </td>
                <td>
                    {{ stat.hs }}%
                </td>
            </tr>
            <tr v-if="!statsView?.stats?.length">
                <td colspan="7" class="text-center">
                    No stats found
                </td>
            </tr>
        </tbody>
    </v-table>
  </v-container>
</template>

<script>
import { GameStatsView } from '@/api/model/models'
import PlayerWidget from '../widgets/PlayerWidget.vue'
export default {
  components: { PlayerWidget },
    props: ['team'],
    data() {
        return {
            statsView: null,
        }
    },
    watch: {
        team() {
            this.statsView = new GameStatsView({in_game_team_id: this.team.id})
            console.log("Stats View: ", this.statsView);
        }
    }
}
</script>

<style>

</style>