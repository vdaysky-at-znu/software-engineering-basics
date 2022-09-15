<template>
    <v-container>
        <v-row v-for="(player, i) in players" :key="i">
            <v-col cols="12" sm="6" md="4" lg="3" xl="2" :key="i">
                <player-widget :player="player"></player-widget>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import PlayerWidget from '../widgets/PlayerWidget.vue'
export default {
  components: { PlayerWidget },
  props: ['players'],

}
</script>

<style>

</style>