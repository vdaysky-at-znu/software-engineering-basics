<template>
  <v-container>
    <div class="text-center mb-3">
      <h2>
        Events
      </h2>
    </div>
    
    <contextual-list v-bind="$attrs" :listComponent="EventsList" propname="events" :source="event">
      <template v-slot:createForm>
        <slot name="createForm">
        </slot>
      </template>
    </contextual-list>
  </v-container>
</template>

<script>
import ContextualList from './ContextualList.vue'
import EventsList from '@/components/lists/EventsList.vue'

export default {
    setup() {
        return {
            EventsList
        }
    },
    components: { ContextualList },
}
</script>

<style>

</style>