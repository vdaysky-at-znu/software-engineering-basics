import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import MsApi from './api/api.js'

loadFonts()

const reactiveModels = {
  install(Vue) {
    Vue.config.globalProperties.$api = MsApi;
    Vue.config.globalProperties.$models = store.state.$models;
    Vue.config.globalProperties.$socket = store.state.$socket;
    Vue.config.globalProperties.$Vue = Vue;

    window.$api = Vue.config.globalProperties.$api;
    window.$models = Vue.config.globalProperties.$models;
    window.$socket = Vue.config.globalProperties.$socket;
    window.$Vue = Vue;

    window.$socket.onEvent("ModelUpdateEvent", (data) => {
      let modelName = data.payload.model_name;
      let modelId = data.payload.model_pk;
      let model = window.$models.get(modelName, modelId);
  
      if (!model) return;
  
      model.load();
    });
    
    window.$socket.onEvent("ModelCreateEvent", (data) => {
      let modelName = data.payload.model_name;
      let modelId = data.payload.model_pk;
      let model = new window.$registeredModels[modelName](modelId);
      window.$models.get("all", modelName).push(model);
    });

  }
}

Array.prototype.remove = function(callback) {
  var i = this.length;
  while (i--) {
      if (callback(this[i], i)) {
          this.splice(i, 1);
      }
  }
};


const app = createApp(App);
console.log(app);
app.use(router)
  .use(store)
  .use(vuetify)
  .use(reactiveModels)
  .mount('#app')
