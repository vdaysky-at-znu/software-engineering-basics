<template>
  <team-sub-view :team="team"></team-sub-view>
</template>

<script>
import { Team } from "@/api/model/models";
import TeamSubView from "@/components/subview/TeamSubView.vue";

export default {
  components: { TeamSubView },
  data() {
    return {
      team: new Team(this.$route.params.team),
    };
  },
};
</script>

<style>
</style>