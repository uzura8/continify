import 'bulma/css/bulma.min.css'
import '@/scss/style.scss'

import { createApp } from 'vue'
import App from '@/App.vue'
import store from './store'
import router from '@/router'
import i18n from '@/i18n'
import PrimeVue from 'primevue/config'
import VueClipboard from 'vue3-clipboard'
import Vue3Sanitize from 'vue-3-sanitize'

const app = createApp(App)
app.use(router)
app.use(store)
app.use(i18n)
app.use(PrimeVue)
app.use(VueClipboard, {
  autoSetContainer: true,
  appendToBody: true
})

app.use(Vue3Sanitize, {
  allowedTags: ['br', 'a'],
  allowedAttributes: {
    a: ['class', 'href', 'target', 'rel', 'title']
  }
})
app.mount('#app')
