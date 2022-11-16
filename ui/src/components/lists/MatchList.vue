<template>
  <contextual-list
    :headers="[
      { name: 'match', label: 'Match' },
      { name: 'team_one', label: 'Team A' },
      { name: 'vs', label: 'VS' },
      { name: 'team_two', label: 'Team B' },
    ]"
    :source="matches"
    v-bind="{...$attrs}"
  >
    <template v-slot:row="{ row, headers }">
      <td v-if="headers.match">
        <match-widget :match="row"></match-widget>
      </td>
      <td v-if="headers.team_one">
        <team-widget
          class="text-center"
          v-if="row.team_one"
          :team="row.team_one"
        ></team-widget>
      </td>
      <td v-if="headers.vs" class="text-center" cols="2">
        <span style="font-size: smaller; font-weight: bold">VS</span>
      </td>
      <td v-if="headers.team_two">
        <team-widget
          class="text-center"
          v-if="row.team_two"
          :team="row.team_two"
        ></team-widget>
      </td>
    </template>
  </contextual-list>
</template>

<script>
import MatchWidget from "@/components/widgets/MatchWidget.vue";
import TeamWidget from "../widgets/TeamWidget.vue";
import ContextualList from "../contextual/ContextualList.vue";

export default {
  components: { MatchWidget, TeamWidget, ContextualList },
  props: ["matches"],
};
</script>

<style>
</style>