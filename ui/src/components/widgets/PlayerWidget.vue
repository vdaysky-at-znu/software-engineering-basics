<template>
  <v-row>
      player {{ player.uuid }}
  </v-row>
</template>

<script>
export default {
    props: ['player'],

    data() {
        return {
        }
    },
    created() { 
    }
}
</script>

<style>

</style>