<template>
  <v-container>
      <team-list :teams="teams"></team-list>
  </v-container>
</template>

<script>
import TeamList from '@/components/lists/TeamList.vue'
import { Team } from '@/api/model/models'
export default {
  components: { TeamList },
  data() {
      return {
          teams: Team.all(),
      }
  }

}
</script>

<style>

</style>