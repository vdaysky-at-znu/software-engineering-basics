<template>
  <v-container>
    <v-card>
      <v-card-title class="justify-center">
        <span>{{ team.full_name }} | {{ team.elo }} Elo </span>
      </v-card-title>
      <v-card-text class="pt-0">
        <contextual-list
          v-bind="$attrs"
          :listComponent="PlayerList"
          :source="team.members"
          propname="players"
        >
        </contextual-list>

      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import PlayerList from "@/components/lists/PlayerList.vue";
import ContextualList from "@/components/contextual/ContextualList.vue";
export default {
    components: { ContextualList },
    setup() {
        return {
            PlayerList,
        }
    },
    props: {'team': null},

}
</script>

<style>

</style>