<template>
  <v-dialog v-model="dialog">

    <template v-slot:activator="{ props }">
      <slot name="button">
          <v-btn v-bind="{...props, ...$attrs}" flat> {{ button }} </v-btn>
      </slot>
    </template>

    <v-card style="width: min(90vw, 800px)">

      <v-card-title>
        {{ title }}
      </v-card-title>
      
      <v-card-content>
        <slot name="content"></slot>
      </v-card-content>

      <v-card-actions>
        <slot name="actions">
          <v-btn @click="dialog = false"> Cancel </v-btn>
          <v-btn @click="$emit('submit')" > submit </v-btn>
        </slot>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {

  inheritAttrs: false,
  props: ['button', 'title'],

  data: () => ({
    dialog: false,
  }),
  watch: {

  },
  methods: {
    close() {
      this.dialog = false
    }
  }
};
</script>

<style>
</style>