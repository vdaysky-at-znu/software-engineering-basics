<template>
  <v-container>
    <contextual-list :source="pubs.games" propname="games" :listComponent="GameList" paginated interactive>

    </contextual-list>
  </v-container>
</template>

<script>
import { PubsView } from '@/api/model/models'
import ContextualList from '@/components/contextual/ContextualList.vue'
import GameList from '@/components/lists/GameList.vue'
export default {

    setup() {
        return {
            GameList
        }
    },

    components: { ContextualList },
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