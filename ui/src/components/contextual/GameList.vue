<template>
  <contextual-list variant="cards" v-if="games" :source="games" :listComponent="GameListDisplay" propname="games" paginated interactive>
  </contextual-list>
</template>

<script>
import ContextualList from './ContextualList.vue'
import GameListDisplay from '@/components/lists/GameListDisplay.vue'
export default {

    setup() {
        return {
            GameListDisplay
        }
    },
  components: { ContextualList },
  props: ['games']

}
</script>

<style>

</style>