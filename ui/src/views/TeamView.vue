<template>
  <team-sub-view :team="team"></team-sub-view>
</template>

<script>
import { Team } from "@/api/model/models";
import TeamSubView from "@/components/subview/TeamSubView.vue";

export default {
  components: { TeamSubView },

  computed: {
    teamId() {
      return this.$route.params.team;
    },
    team() {
      return new Team(this.teamId);
    },
  },
};
</script>

<style>
</style>