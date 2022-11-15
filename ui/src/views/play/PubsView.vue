<template>
  <v-container>
    <game-list :games="pubs.games" paginated interactive>

    </game-list>
  </v-container>
</template>

<script>
import { PubsView } from '@/api/model/models'
import GameList from '@/components/contextual/GameList.vue'
export default {

    setup() {
        return {
            GameList
        }
    },

    components: { GameList },
    data() { 
        return {
            pubs: null,
        }
    },

    created() {
        this.pubs = new PubsView({});
    }
}
</script>

<style>

</style>