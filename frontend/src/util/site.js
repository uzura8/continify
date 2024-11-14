import * as bulmaToast from 'bulma-toast'
import config from '@/config/config'
import str from './str'
import obj from './obj'
import common from './common'
import media from './media'

const IS_DEBUG = obj.getVal(config, 'isDebug', false)

export default {
  uri: (path) => {
    const validPath = str.ltrimChar(path, '/')
    const domain = config.domain
    const port = config.port ? ':' + config.port : ''
    const basePath = config.baseUrl
    if (!domain && !port) return basePath + validPath

    const schem = config.isSSL ? 'https://' : 'http://'
    let items = [schem, domain, port, basePath, validPath]
    return items.join('')
  },

  absUri: (path) => {
    const validPath = str.ltrimChar(path, '/')
    const domain = config.domain ? config.domain : window.location.host
    if (common.isEmpty(domain)) return

    const port = config.port ? ':' + config.port : ''
    const basePath = config.baseUrl
    const schem = config.isSSL ? 'https://' : 'http://'
    let items = [schem, domain, port, basePath, validPath]
    return items.join('')
  },

  baseUri: (type = 'url') => {
    const domain = config.domain
    const port = config.port ? ':' + config.port : ''
    const basePath = config.baseUrl
    if (!domain && !port) return basePath

    const schem = config.isSSL ? 'https://' : 'http://'
    let items = [domain, port]

    if (type == 'host') return items.join('')
    items.unshift(schem)
    if (type == 'origin') return items.join('')
    items.push(basePath)
    return items.join('')
  },

  assetUri: (path) => {
    let items = [path]
    items.unshift(config.media.url)
    return items.join('/')
  },

  mediaUrl: (serviceId, type, fileId, mimeType, size = 'raw') => {
    const ext = media.getExtensionByMimetype(mimeType)
    let pathItems = [config.media.url, serviceId]
    if (type === 'image') {
      const fileName = `${size}.${ext}`
      pathItems.push('images', fileId, fileName)
    } else {
      const fileName = `${fileId}.${ext}`
      pathItems.push('docs', fileName)
    }
    return pathItems.join('/')
  },

  checkResponseHasErrorMessage: (err, isFieldsErrors = false) => {
    if (err == null) return false
    if ('response' in err === false || err.response == null) return false
    if ('data' in err.response === false || err.response.data == null) return false
    if (isFieldsErrors) {
      return err.response.data.errors != null
    }
    return err.response.data.message != null
  },

  showGlobalMessage(msg, type = 'is-danger', pos = 'bottom-center', duration = 5000) {
    bulmaToast.toast({
      message: msg,
      type: type,
      dismissible: true,
      position: pos,
      opacity: 0.9,
      duration: duration,
      aimate: { in: 'fadeInUp', out: 'fadeOutDown' },
      extraClasses: 'u-min-width-400'
    })
  },

  debugOutput(data) {
    if (IS_DEBUG === false) return
    console.log(data)
  }
}
