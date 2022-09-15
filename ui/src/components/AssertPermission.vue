<template>
  <div v-show="show">
    <slot></slot>
  </div>
</template>

<script>
export default {
    props: ['permission'],

    computed: {
        show() {
            return this.$store.state.player && this.$store.state.player.hasPermission(this.permission);
        }
    }
}
</script>

<style>

</style>