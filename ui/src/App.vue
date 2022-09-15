<template>

  <v-app ref="app">
    <v-app-bar color="grey-lighten-2">
      <template v-slot:prepend>
          <v-app-bar-nav-icon v-show="!smAndUp" @click.stop="wide = !wide"></v-app-bar-nav-icon>
      </template>
        
      <v-app-bar-title @click="$router.push({name: 'home'})">BetterMS</v-app-bar-title>
      <v-spacer></v-spacer>

      <div v-show="smAndUp">
        <v-btn :to="{name: 'players'}" flat>Players</v-btn>
        <v-btn :to="{name: 'teams'}" flat>Teams</v-btn>
        <v-btn :to="{name: 'events'}" flat>Events</v-btn>
      </div>

      <v-spacer></v-spacer>
      <div v-if="!$store.state.player">
        <AuthForm>

        </AuthForm>
      </div>
      <div v-else>
        <ProfileLink></ProfileLink>
      </div>

    </v-app-bar>
    <v-navigation-drawer v-model="wide" color="grey-darken-2" temporary>
      <v-list>
        <v-list-item><v-btn flat>Players</v-btn></v-list-item>
        <v-list-item><v-btn flat>Teams</v-btn></v-list-item>
        <v-list-item><v-btn flat>Events</v-btn></v-list-item>
        <v-list-item><v-btn flat>Results</v-btn></v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-navigation-drawer color="grey-darken-2"></v-navigation-drawer>
    <v-navigation-drawer color="grey-darken-2" position="right"></v-navigation-drawer>
    <v-main>
      <router-view></router-view>
    </v-main>

  </v-app>
</template>

<script>
import { useDisplay } from 'vuetify'
import AuthForm from './components/AuthForm.vue';
import API from './api/api';
import ProfileLink from './components/ProfileLink.vue';

export default {
  name: 'App',

  components: {AuthForm, ProfileLink}, 

  data: () => ({
    wide: false,
    left_active: true,
  }),

  async created() {
      let player = await API.getMe();
      this.$store.commit('setPlayer', player);
  },

  setup () {
    const { xs, smAndUp } = useDisplay()
    return { xs, smAndUp }
  },
}
</script>
