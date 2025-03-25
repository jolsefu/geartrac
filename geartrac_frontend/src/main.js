import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

import GAuth from 'vue-google-oauth2'

const app = createApp(App)

app.use(router, GAuth)

app.mount('#app')
