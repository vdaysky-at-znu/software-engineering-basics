<template>
  <v-container>
    <v-table>
        <thead>
            <tr>
                <th class="text-left">
                    Match
                </th>
                <th class="text-center">
                    Team A
                </th>
                <th>
                    
                </th>
                <th class="text-center">
                    Team B
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="match in matches" :key="match.id">
                <td>
                    <match-widget v-if="match.name" :match="match"></match-widget>
                </td>
                <td>
                    <team-widget class="text-center" v-if="match.team_one" :team="match.team_one"></team-widget>
                </td>
                <td class="text-center" cols="2">
                    <span style="font-size: smaller; font-weight: bold;">VS</span>
                </td>
                <td>
                    <team-widget class="text-center" v-if="match.team_two" :team="match.team_two"></team-widget>
                </td>
            </tr>
        </tbody>
    </v-table>
  </v-container>
</template>

<script>
import MatchWidget from "@/components/widgets/MatchWidget.vue"
import TeamWidget from '../widgets/TeamWidget.vue'

export default {
    components: { MatchWidget, TeamWidget },
    props: ['matches']
}
</script>

<style>

</style>