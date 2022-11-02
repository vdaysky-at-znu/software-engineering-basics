<template>
  <v-row class="flex-nowrap">
    <v-col cols="auto" class="d-flex align-center" :class="{'pa-0': dense}">
        <player-avatar v-bind="{...$attrs, ...$props}" :player="player"></player-avatar>
    </v-col>
    <v-col style="width: 1px">
        <div class="d-flex align-center" style="height: 100%">
            <router-link class="w-100 text-truncate" v-if="player?.id" :to="{name: 'player', params: {id: player.id} }" >
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
    props: {'player': null, dense: Boolean},

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