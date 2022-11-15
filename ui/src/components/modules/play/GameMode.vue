<template>
  <v-card min-width="200px" max-width="400px" class="d-flex flex-column">
    <v-card-title>
      {{ name }}
    </v-card-title>
    <v-divider class="mb-2"></v-divider>
    <v-card-subtitle class="d-flex justify-space-between">
      <p>
        <b>{{ online }}</b> Players Online
      </p>
      <p>
        <b>{{ lobbies }}</b> Active Lobbies
      </p>
    </v-card-subtitle>
    
    <v-card-content height="100px">
      {{ description }}
    </v-card-content>
    <v-spacer></v-spacer>
    <v-card-actions>
      <v-btn block variant="outlined" color="primary" @click="$emit('selected')">Play!</v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: ["name", "description", "online", "lobbies"],
};
</script>

<style>
</style>