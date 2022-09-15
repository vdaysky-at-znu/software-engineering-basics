<template>
  <router-link :to="{name: 'profile'}">
    {{ $store.state.player.username || $store.state.player.uuid }}
  </router-link>
</template>

<script>
export default {

}
</script>

<style>

</style>