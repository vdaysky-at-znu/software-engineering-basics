<template>
    <v-container>
        <v-table>
            <thead>
                <tr>
                    <th >
                        #
                    </th>
                    <th>
                        Player
                    </th>
                    <th v-if="!dense">
                        Elo
                    </th>
                    <th v-if="!hideTeam && !dense">
                        Team
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(player, i) in players" :key="player">
                    <td width="8%">
                        {{ i + 1 }}.
                    </td>
                    <td>
                        <player-widget v-bind="{...$props, ...$attrs}" :player="player"></player-widget>
                    </td>
                    <td v-if="!dense">
                        {{ player.elo }}
                    </td>
                    <td v-if="!hideTeam && !dense">
                        <team-widget v-if="player.team" :team="player.team"></team-widget>
                    </td>
                </tr>
            </tbody>
        </v-table>
    </v-container>
</template>

<script>
import PlayerWidget from '../widgets/PlayerWidget.vue'
import TeamWidget from '../widgets/TeamWidget.vue'
export default {
  components: { PlayerWidget, TeamWidget },
  props: {
    'players': Object, 
    'hideTeam': Boolean,
    dense: Boolean,
  },
}
</script>

<style>

</style>