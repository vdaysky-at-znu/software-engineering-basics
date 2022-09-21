<template>
  <v-img max-height="32px" max-width="32px" min-height="32px" min-width="32px" v-if="player.uuid" :src="`https://crafatar.com/avatars/${player.uuid}`"></v-img> 
</template>

<script>
export default {
    props: ['player']
}
</script>

<style>

</style>