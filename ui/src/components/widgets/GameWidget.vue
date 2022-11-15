<template>
  <router-link :to="{name: 'game', params: {'id': game.id} }"> {{ game?.map?.display_name }} {{ score }} </router-link>
</template>

<script>
export default {
    props: ['game'],
    computed: {
        score() {
            if (this.game.is_started) {
                return "(" + this.game.score_a + ' - ' + this.game.score_b + ")"
            }
            return ""
        }
    }
}
</script>

<style>

</style>