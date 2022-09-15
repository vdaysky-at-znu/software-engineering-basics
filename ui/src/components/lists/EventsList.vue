<template>
  <v-container>
        <v-row v-for="(event, i) in events" :key="i">
            <v-col cols="12" sm="6" md="4" lg="3" xl="2" :key="i">
                <event-widget :event="event"></event-widget>
            </v-col>
        </v-row>
  </v-container>
</template>

<script>
import EventWidget from "../widgets/EventWidget.vue"

export default {
    props: ['events'],
    components: { EventWidget },
}
</script>

<style>

</style>