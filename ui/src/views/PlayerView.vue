<template>
    <v-container>
          <player-widget :player="player"></player-widget>
    </v-container>
</template>

<script>
import PlayerWidget from '@/components/widgets/PlayerWidget.vue'
import { Player } from '@/api/model/models.js';

export default {
  components: { PlayerWidget },
    data() {
        return {
            player: new Player(this.$route.params.id),
        }
    },
}
</script>

<style>

</style>