import { createI18n } from 'vue-i18n'
import messages from '@intlify/unplugin-vue-i18n/messages'

//import en from './translations/en'
//import ja from './translations/ja'

//const messages = {
//  en,
//  ja
//}

const i18n = createI18n({
  locale: window.navigator.language,
  //allowComposition: true, // you need to specify that!
  legacy: false,
  globalInjection: true,
  fallbackLocale: 'en',
  availableLocales: ['en', 'ja'],
  messages,
})

export default i18n
