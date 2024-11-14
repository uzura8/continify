import { resolve, dirname } from 'path'
import { fileURLToPath, URL } from 'node:url'
import VueI18nPlugin from '@intlify/unplugin-vue-i18n/vite'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import postcssNesting from 'postcss-nesting'

const config = {
  plugins: [
    vue(),
    VueI18nPlugin({
      // locale messages resource pre-compile option
      include: resolve(dirname(fileURLToPath(import.meta.url)), './src/i18n/translations/**'),
      strictMessage: false,
    }),
  ],
  define: {
    //__VUE_I18N_FULL_INSTALL__: false,
    //__VUE_I18N_LEGACY_API__: false,
    //__INTLIFY_PROD_DEVTOOLS__: false
  },
  resolve: {
    extensions: ['.js', '.json', '.vue'],
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
  //publicDir: 'static',
  publicDir: 'src/assets',
  build: {
    outDir: 'public',
    //sourcemap: 'inline',
  },
  css: {
    postcss: {
      plugins: [postcssNesting]
    }
  },
    preprocessorOptions: {
    scss: {
      additionalData: `@import "./src/scss/style.scss";`
    }
  }
}

if (process.env.NODE_ENV !== 'production') {
  config.define.global = {}
}

export default defineConfig(config)

