<template>
  <v-container>
    <v-card>
      <v-card-title class="justify-center">
        <span>{{ title }}</span>
      </v-card-title>
      <v-card-text class="pt-0">
        <contextual-list
          v-bind="dynamicProps"
          :listComponent="PlayerList"
          :source="players"
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
import { MatchTeam } from '@/api/model/models';
export default {
    components: { ContextualList },
    setup() {
        return {
            PlayerList,
        }
    },
    props: {'team': null},
    computed: {
      isMatchTeam() {
        return this.team instanceof MatchTeam;
      },
      title() {
        if (this.isMatchTeam) {
          return this.team.name;
        }
        return this.team.short_name + " | " + this.team.elo + " Elo"; 
      },
      players() {
        if (this.isMatchTeam) {
          return this.team.players;
        }
        return this.team.members;
      },
      dynamicProps() {
        let a = {...this.$attrs};
        delete a['style'];
        return a;
      }
    }

}
</script>

<style>

</style>