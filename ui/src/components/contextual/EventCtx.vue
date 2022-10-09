<template>
  <v-container>
    <div class="text-center mb-3">
      <h2>
        {{ event.name }}
      </h2>
    </div>
    
    <contextual-list v-bind="$attrs" :listComponent="MatchList" propname="matches" :source="event.matches">
      <template v-slot:createForm>
        <slot name="createForm">
        </slot>
      </template>
    </contextual-list>
  </v-container>
</template>

<script>
import ContextualList from './ContextualList.vue'
import MatchList from '@/components/lists/MatchList.vue'
export default {
  components: { ContextualList },
  setup() {
    return {
        MatchList,
    }
  },
  props: ['event'],

}
</script>

<style>

</style>