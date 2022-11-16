<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Teams</h1>
        <code> {{ teams.count }} teams found </code>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <team-list :teams="teams" interactive paginated></team-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { Team } from "@/api/model/models";
import TeamList from '@/components/lists/TeamList.vue';
export default {
  components: { TeamList },
  data() {
    return {
      teams: Team.all(),
    };
  },
};
</script>

<style>
</style>