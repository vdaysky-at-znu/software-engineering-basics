<template>
  <v-img 
    :max-height="dense ? '24px' : '32px'" 
    :max-width="dense ? '24px' : '32px'" 
    :min-height="dense ? '24px' : '32px'" 
    :min-width="dense ? '24px' : '32px'" 
    style="{'padding': '0px'}"
    v-if="player.uuid" 
    :src="`https://crafatar.com/avatars/${player.uuid}`">
  </v-img> 
</template>

<script>
export default {
    props: {
      'player': null, 
      'dense': Boolean
    },
}
</script>

<style>

</style>