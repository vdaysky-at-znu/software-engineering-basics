<template>
  <v-container>
        <v-table>
            <thead>
                <tr>
                    <th class="text-left">
                        Map
                    </th>
                    <th class="text-right">
                        Status
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="game in games" :key="game.id">
                    <td>
                        <game-widget :game="game"></game-widget>
                    </td>
                    <td class="text-end">
                        <p v-if="game.is_finished">Finished</p>
                        <p v-else-if="game.is_started">Live</p>
                        <p v-else>Upcoming</p>
                    </td>
                </tr>
            </tbody>
        </v-table>
  </v-container>
</template>

<script>
import GameWidget from "../widgets/GameWidget.vue"

export default {
    components: { GameWidget },
    props: ['games']
}
</script>

<style>

</style>