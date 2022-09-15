<template>
  <v-container>
      <h3> {{ event.name }} </h3>
  </v-container>
</template>

<script>
import { Event } from '@/api/model/models'
export default {
    data() {
        return {
            event: new Event(this.$route.params.event)
        }
    }
}
</script>

<style>

</style>