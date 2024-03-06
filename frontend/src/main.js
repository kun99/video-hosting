import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { library } from '@fortawesome/fontawesome-svg-core'

/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faBell, faHeart, faEye } from '@fortawesome/free-solid-svg-icons'

library.add(faBell, faHeart, faEye)

import App from './App.vue'
import router from './router'
import './index.css'
import 'video.js/dist/video-js.css';

const app = createApp(App).component('font-awesome-icon', FontAwesomeIcon)

import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

app.use(createPinia().use(piniaPluginPersistedstate))
app.use(router)

app.mount('#app')
