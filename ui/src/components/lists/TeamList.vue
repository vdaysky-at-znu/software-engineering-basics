<template>
  <contextual-list
    :source="teams"
    :headers="[
      { label: '#', name: 'index' },
      { label: 'Team', name: 'team' },
      { label: 'Elo', name: 'elo', orderable: true },
    ]"
  >
    <template v-slot:row="{ i, row, headers }">
      <td v-if="headers.index" width="8%">{{ i + 1 }}.</td>
      <td v-if="headers.team">
        <team-widget :team="row"></team-widget>
      </td>
      <td v-if="headers.elo">
        {{ row.elo }}
      </td>
    </template>
  </contextual-list>
</template>

<script>
import ContextualList from "../contextual/ContextualList.vue";
import TeamWidget from "../widgets/TeamWidget.vue";
export default {
  props: ["teams"],
  components: {
    TeamWidget,
    ContextualList,
  },
};
</script>

<style>
</style>