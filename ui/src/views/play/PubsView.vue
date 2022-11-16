<template>
  <v-container>
    <game-list variant='cards' :games="pubs.games" paginated interactive>

    </game-list>
  </v-container>
</template>

<script>
import { PubsView } from '@/api/model/models'
import GameList from '@/components/lists/GameList.vue'
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