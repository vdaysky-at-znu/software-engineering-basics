<template>
  <div>

    <router-link :to="{name: 'team', params: {team: team.id} }">
        {{ team.short_name }}
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