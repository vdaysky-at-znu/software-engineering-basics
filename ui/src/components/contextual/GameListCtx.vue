<template>
  <contextual-list v-if="source" :source="source" :listComponent="GameList" propname="games" paginated interactive>
  </contextual-list>
</template>

<script>
import ContextualList from './ContextualList.vue'
import GameList from '@/components/lists/GameList.vue'
export default {

    setup() {
        return {
            GameList
        }
    },
  components: { ContextualList },
  props: ['source']

}
</script>

<style>

</style>