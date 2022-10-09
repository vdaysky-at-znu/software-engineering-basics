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
        <contextual-list :source="teams" :listComponent="TeamList" propname="teams" interactive paginated></contextual-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import TeamList from "@/components/lists/TeamList.vue";
import { Team } from "@/api/model/models";
import ContextualList from '@/components/contextual/ContextualList.vue';
export default {
  components: { ContextualList },
  setup() {
    return {
      TeamList
    }
  },
  data() {
    return {
      teams: Team.all(),
    };
  },
};
</script>

<style>
</style>