<template>
  <v-dialog v-model="dialog">

    <template v-slot:activator="{ props }">
          <v-btn v-bind="props" flat> {{ button }} </v-btn>
        </template>

    <v-card style="width: min(90vw, 800px)">

      <v-card-title>
        {{ title }}
      </v-card-title>
      
      <v-card-content>
        <slot name="content"></slot>
      </v-card-content>

      <v-card-actions>
        <v-btn @click="dialog = false"> Cancel </v-btn>
        <v-btn > submit </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {

  props: ['button', 'title'],

  data: () => ({
    dialog: false,
  }),
};
</script>

<style>
</style>