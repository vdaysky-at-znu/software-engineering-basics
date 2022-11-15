import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import PlayerView from '../views/PlayerView.vue'
import TeamView from '../views/TeamView.vue'
import TeamsView from '../views/TeamsView.vue'
import PlayersView from '../views/PlayersView.vue'
import EventView from '../views/EventView.vue'
import EventsView from '../views/EventsView.vue'
import MyProfileView from '../views/MyProfileView.vue'
import MatchView from '../views/MatchView.vue'
import GameView from '../views/GameView.vue'
import PlayView from '../views/PlayView.vue'
import RankedView from '../views/play/RankedView.vue'
import PubsView from '../views/play/PubsView.vue'
import DeathmatchView from '../views/play/DeathmatchView.vue'
import DuelsView from '../views/play/DuelsView.vue'
import RankedQueueView from '../views/play/ranked/RankedQueueView.vue'
import PostView from '../views/PostView.vue'

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
    component: MyProfileView,
  }, 
  {
    path: '/match/:id',
    name: 'match',
    component: MatchView,
  }, 
  {
    path: '/game/:id',
    name: 'game',
    component: GameView,
  },
  {
    path: '/play',
    name: 'play',
    component: PlayView,
  },
  {
    path: '/play/deathmatch',
    name: 'deathmatch',
    component: DeathmatchView,
  },
  {
    path: '/play/ranked',
    name: 'ranked',
    component: RankedView,
  },
  {
    path: '/play/pubs',
    name: 'pubs',
    component: PubsView,
  },
  {
    path: '/play/duels',
    name: 'duels',
    component: DuelsView,
  },
  {
    path: '/ranked/queue/:id',
    name: 'ranked-queue',
    component: RankedQueueView,
  },
  {
    path: '/post/:id',
    name: 'post',
    component: PostView,
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
