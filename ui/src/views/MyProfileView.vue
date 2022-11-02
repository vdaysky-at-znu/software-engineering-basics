<template>
  <player-profile :player="me" :own="true"></player-profile>
</template>

<script>
import PlayerProfile from '@/components/common/PlayerProfile.vue'
export default {
  components: { PlayerProfile },
  computed: {
    me() {
        return this.$store.state.player;
    }
  }

}
</script>

<style>

</style>