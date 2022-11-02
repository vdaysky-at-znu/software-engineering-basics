<template>
  <v-container>
    <v-row>
      <v-col>
        <h1>Ranked</h1>
        <code> {{ ranked.queues.count }} ranked queues found </code>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="queue in ranked.queues" :key="queue.id">
        <v-card class="d-flex flex-column">
          <v-card-title>
            <h2>Ranked Queue #{{ queue.id }}</h2>
            <v-chip color="green" v-if="!queue.locked">
                Opened
            </v-chip>
            <v-chip color="red" v-else>
                Locked
            </v-chip>
            <v-chip color="green" v-if="queue.id == ranked?.my_queue?.id">
              You are in
            </v-chip>
          </v-card-title>
          <v-card-content>
            <code> {{ queue.players.count }} / 10 Players </code>
            
          </v-card-content>
          <v-spacer></v-spacer>
          <v-card-actions>
            <v-col>
              <v-btn :to="{name: 'ranked-queue', params: {id: queue.id} }" >Open Queue</v-btn>
            </v-col>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { RankedView } from "@/api/model/models";
export default {
  data() {
    return {
      ranked: null,
    };
  },

  created() {
    this.ranked = new RankedView({});
  },
};
</script>

<style>
</style>