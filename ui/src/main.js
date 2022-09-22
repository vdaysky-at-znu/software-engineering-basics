import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import vuetify from './plugins/vuetify'
import { loadFonts } from './plugins/webfontloader'
import MsApi from './api/api.js'
import Datepicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'

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
Date.prototype.toJSON = function () {
  var timezoneOffsetInHours = -(this.getTimezoneOffset() / 60); //UTC minus local time
  var sign = timezoneOffsetInHours >= 0 ? '+' : '-';
  var leadingZero = (Math.abs(timezoneOffsetInHours) < 10) ? '0' : '';

  //It's a bit unfortunate that we need to construct a new Date instance 
  //(we don't want _this_ Date instance to be modified)
  var correctedDate = new Date(this.getFullYear(), this.getMonth(), 
      this.getDate(), this.getHours(), this.getMinutes(), this.getSeconds(), 
      this.getMilliseconds());
  correctedDate.setHours(this.getHours() + timezoneOffsetInHours);
  var iso = correctedDate.toISOString().replace('Z', '');

  return iso + sign + leadingZero + Math.abs(timezoneOffsetInHours).toString() + ':00';
}


const app = createApp(App);

app.component('vDatepicker', Datepicker);


app.use(router)
  .use(store)
  .use(vuetify)
  .use(reactiveModels)
  .mount('#app')
