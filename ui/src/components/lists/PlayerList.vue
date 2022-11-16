<template>
  <contextual-list
    v-bind="{...$attrs}"
    :source="players"
    :headers="[
      { label: '#', name: 'index' },
      { label: 'Player', name: 'player' },
      { label: 'Elo', name: 'elo', orderable: true },
      { label: 'Team', name: 'team'},
    ]"
  >
    <template v-slot:row="{ i, row, headers }">
      <td v-if="headers.index" width="8%">{{ i + 1 }}.</td>
      <td>
        <player-widget :player="row"></player-widget>
      </td>
      <td v-if="headers.elo">
        {{ row.elo }}
      </td>
      <td v-if="headers.team">
        <team-widget v-if="row.team" :team="row.team"></team-widget>
      </td>
    </template>
  </contextual-list>
</template>

<script>
import ContextualList from "../contextual/ContextualList.vue";
import PlayerWidget from "../widgets/PlayerWidget.vue";
import TeamWidget from "../widgets/TeamWidget.vue";
export default {
  components: { PlayerWidget, TeamWidget, ContextualList },
  props: {
    players: Object,
    hideTeam: Boolean,
    dense: Boolean,
  },
};
</script>

<style>
</style>