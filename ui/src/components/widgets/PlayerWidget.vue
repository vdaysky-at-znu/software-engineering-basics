<template>
  <v-row>
    <v-col cols="auto">
        <player-avatar :player="player"></player-avatar>
    </v-col>
    <v-col>
        <div class="d-flex align-center" style="height: 100%">
            <router-link v-if="player?.id" :to="{name: 'player', params: {id: player.id} }" >
                {{ player.username }}
            </router-link>
        </div>
        
    </v-col>
      
  </v-row>
</template>

<script>
import playerAvatar from '../atom/player-avatar.vue'
export default {
  components: { playerAvatar },
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