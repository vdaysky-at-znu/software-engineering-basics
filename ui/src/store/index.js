import { ModelManager } from '@/api/model/model'
import { SocketConnection } from '@/api/utils'
import { createStore } from 'vuex'


export default createStore({
  state: {
    $models: new ModelManager(),
    $socket: new SocketConnection(),
    player: null,
  },
  getters: {
  },
  mutations: {
    setPlayer(state, player) {
      state.player = player;
    }
  },
  actions: {
  },
  modules: {
  }
})
