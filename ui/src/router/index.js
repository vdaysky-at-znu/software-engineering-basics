import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlayerView from '../views/PlayerView.vue'
import TeamView from '../views/TeamView.vue'
import TeamsView from '../views/TeamsView.vue'
import PlayersView from '../views/PlayersView.vue'
import EventView from '../views/EventView.vue'
import EventsView from '../views/EventsView.vue'
import MyProfile from '../views/MyProfile.vue'
import MatchView from '../views/MatchView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView
  },
  {
    path: '/player/:id',
    name: 'player',
    component: PlayerView,
  },
  {
    path: '/team/:team',
    name: 'team',
    component: TeamView,
  },
  {
    path: '/teams',
    name: 'teams',
    component: TeamsView,
  },
  {
    path: '/players',
    name: 'players',
    component: PlayersView,
  },
  {
    path: '/event/:event',
    name: 'event',
    component: EventView,
  },
  {
    path: '/events',
    name: 'events',
    component: EventsView,
  },
  {
    path: '/profile',
    name: 'profile',
    component: MyProfile,
  }, 
  {
    path: '/match/:id',
    name: 'match',
    component: MatchView,
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
