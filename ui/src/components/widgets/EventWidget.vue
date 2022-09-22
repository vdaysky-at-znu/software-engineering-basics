<template>
  <div>
    <router-link :to="{name: 'event', params: {event: event.id} }">{{ event.name }}</router-link>
  </div>
</template>

<script>

export default {
    props: ['event'],

}
</script>

<style>

</style>