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
                        Elo
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(player, i) in players" :key="player">
                    <td width="8%">
                        {{ i + 1 }}.
                    </td>
                    <td>
                        <player-widget :player="player"></player-widget>
                    </td>
                    <td>
                        {{ player.elo }}
                    </td>
                </tr>
            </tbody>
        </v-table>
    </v-container>
</template>

<script>
import PlayerWidget from '../widgets/PlayerWidget.vue'
export default {
  components: { PlayerWidget },
  props: ['players'],

}
</script>

<style>

</style>