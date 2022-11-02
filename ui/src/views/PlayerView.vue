<template>
    <player-profile :player="player" :own="false"></player-profile>
</template>

<script>
import { Player } from '@/api/model/models.js';
import PlayerProfile from '@/components/common/PlayerProfile.vue';

export default {
  components: { PlayerProfile },
    data() {
        return {
            player: new Player(this.$route.params.id),
        }
    },
}
</script>

<style>

</style>