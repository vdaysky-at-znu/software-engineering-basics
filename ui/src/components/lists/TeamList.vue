<template>
  <v-container>
    <v-table>
        <thead>
            <tr>
                <th>
                    #
                </th>
                <th>
                    Team
                </th>
                <th>
                    Elo
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(team, i) in teams" :key="team">
                <td width="8%">
                    {{ i + 1 }}.
                </td>
                <td>
                    <team-widget :team="team"></team-widget>
                </td>
                <td>
                    {{ team.elo }}
                </td>
            </tr>
        </tbody>
    </v-table>
  </v-container>
</template>

<script>
import TeamWidget from '../widgets/TeamWidget.vue'
export default {
    props: ['teams'],
    components: {
        TeamWidget
    }
}
</script>

<style>

</style>