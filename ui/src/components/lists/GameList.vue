<template>
  <contextual-list 
  :variant="variant"
  :source="games"
  :headers=[]
  :filters="[
    {name: 'map', label: 'Map', type: 'select', options: maps, toOption: map => ({title: map.display_name, value: map.id})},
  ]"
  paginated 
  interactive
  >
  <template v-slot:card="{item}">
    <game-card :game="item" :joinable="joinable"></game-card>
  </template>
  </contextual-list>
</template>

<script>
import GameCard from '../cards/GameCard.vue'
import ContextualList from '../contextual/ContextualList.vue'
import { Map } from '../../api/model/models.js'
export default {
  components: { ContextualList, GameCard },
  props: {
    'games': Object, 
    'variant': String, 
    'joinable': Boolean,
  },

  data() {
    return {
      maps: Map.all()
    }
  },
}
</script>

<style>

</style>