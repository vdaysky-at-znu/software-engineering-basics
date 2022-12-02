<template>
  <div>

    <router-link :to="{name: 'team', params: {team: team?.team?.id || team.id} }">
        {{ team.short_name || team.name }}
    </router-link>
      
  </div>
</template>

<script>
export default {
    props: ['team']
}
</script>

<style scoped>

</style>