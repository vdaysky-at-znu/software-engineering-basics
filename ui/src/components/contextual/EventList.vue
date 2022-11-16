<template>
  <v-container>
    <div class="text-center mb-3">
      <h2>Events</h2>
    </div>
    <contextual-list
      v-bind="$attrs"
      :listComponent="EventsListDisplay"
      propname="events"
      :source="events"
      :filters="[
        { label: 'Upcoming', name: 'upcoming', type: 'boolean' },
        {
          label: 'With Teams',
          name: 'teams_in',
          type: 'select',
          variant: 'multiple',
          options: ['Team A', 'Team B'],
        },
        {
          label: 'Map',
          name: 'map_in',
          type: 'select',
          variant: 'multiple',
          options: ['Map A', 'Map B'],
        },
        {
          label: 'With Players',
          name: 'players_in',
          type: 'select',
          variant: 'multiple',
          options: playerOptions,
          toOption: player => ({title: player.username, value: player.id})
        },
      ]"
      :headers="[
        {label: 'Event', name: 'event', orderable: true, align: 'left'}, 
        {label: 'Date',  name: 'date', orderable: true, align: 'right'}
      ]"
    >
      <template v-slot:createForm>
        <slot name="createForm"> </slot>
      </template>

      <template v-slot:row="{ row }">
        <td>
          <event-widget :event="row"></event-widget>
        </td>
        <td class="text-end">
          {{ row.start_date }}
        </td>
      </template>
    </contextual-list>
  </v-container>
</template>

<script>
import ContextualList from "./ContextualList.vue";
import EventsListDisplay from "@/components/lists/EventsListDisplay.vue";
import EventWidget from '../widgets/EventWidget.vue';
import { Player } from '../../api/model/models.js'

export default {
  setup() {
    return {
      EventsListDisplay, Player
    };
  },
  props: ["events"],
  data() {
    return {
      playerOptions: Player.all(),
    }
  },

  components: { ContextualList, EventWidget },
};
</script>

<style>
</style>