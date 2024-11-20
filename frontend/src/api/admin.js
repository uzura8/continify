import utilCommon from '@/util/common'
import utilUri from '@/util/uri'
import client from './client'

export default {
  getServices: (identifer = '', params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = identifer ? `admin/services/${identifer}` : 'admin/services'
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  checkServiceExists: (identifer, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      client
        .head(`admin/services/${identifer}`, options)
        .then((res) => {
          resolve(res.headers)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  getServiceConfigList: (token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions({}, token)
      const uri = 'admin/services/configs'
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  getServiceConfig: (serviceId, configName, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions({}, token)
      const uri = `admin/services/${serviceId}/configs/${configName}`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  createService: (vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = 'admin/services'
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updateService: (serviceId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/services/${serviceId}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updateServiceConfig: (serviceId, configName, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/services/${serviceId}/configs/${configName}`
      client
        .put(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getServiceContentList: (serviceId, params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/services/${serviceId}/content`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  getServiceContent: (serviceId, contentId, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions({}, token)
      const uri = `admin/services/${serviceId}/content/${contentId}`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  saveServiceContent: (serviceId, contentId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/services/${serviceId}/content/${contentId}`
      client
        .put(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deleteServiceContent: (serviceId, contentId, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/services/${serviceId}/content/${contentId}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getUsers: (identifer = '', params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = identifer ? `admin/users/${identifer}` : 'admin/users'
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  updateUser: (username, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/users/${username}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getPosts: (serviceId, identifer = '', params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = identifer ? `admin/posts/${serviceId}/${identifer}` : `admin/posts/${serviceId}`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  headPostBySlug: (serviceId, identifer = '', token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/${identifer}`
      client
        .head(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  checkPostSlugNotExists: (serviceId, slug, token = null) => {
    return new Promise((resolve, reject) => {
      const params = { slug: slug }
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/posts/${serviceId}/slug`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  createPost: (serviceId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updatePost: (serviceId, identifer, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/${identifer}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updatePostStatus: (serviceId, identifer, postStatus, token = null) => {
    return new Promise((resolve, reject) => {
      const vals = { status: postStatus }
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/${identifer}/status`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deletePost: (serviceId, identifer, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/${identifer}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getPostCacheInfo: (serviceId, identifer, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/${identifer}/cache`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  getPostGroups: (serviceId, identifer = '', params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = identifer
        ? `admin/posts/${serviceId}/groups/${identifer}`
        : `admin/posts/${serviceId}/groups`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  checkPostGroupSlugNotExists: (serviceId, slug, token = null) => {
    return new Promise((resolve, reject) => {
      const params = { slug: slug }
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/posts/${serviceId}/groups/slug`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  createPostGroup: (serviceId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/groups`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updatePostGroup: (serviceId, identifer, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/groups/${identifer}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updatePostGroupPostIdsRegistered: (serviceId, slug, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/groups/${slug}/post-ids`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deletePostGroup: (serviceId, identifer, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/posts/${serviceId}/groups/${identifer}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getAccountServices: (params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = 'admin/account/services'
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  createS3PreSignedUrl: (serviceId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/files/${serviceId}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deleteFile: (serviceId, fileId, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/files/${serviceId}/${fileId}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getCategoryChildrenByParentSlug: (serviceId, slug, params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/categories/${serviceId}/${slug}/children`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  checkCategorySlugNotExists: (serviceId, slug, token = null) => {
    return new Promise((resolve, reject) => {
      const params = { slug: slug }
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/categories/${serviceId}/slug`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  createCategory: (serviceId, vals, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/categories/${serviceId}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updateCategory: (serviceId, identifer, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/categories/${serviceId}/${identifer}`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deleteCategory: (serviceId, identifer, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/categories/${serviceId}/${identifer}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  updateCategoriesOrder: (serviceId, parentCateSlug, vals, token = null) => {
    return new Promise((resolve, reject) => {
      if (utilCommon.isEmpty(vals)) throw new Error('No value')
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/categories/${serviceId}/${parentCateSlug}/children`
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  getCommentList: (serviceId, params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/comments/${serviceId}`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  getCommentListByContent: (serviceId, contentId, params = {}, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(params, token)
      const uri = `admin/comments/${serviceId}/content/${contentId}`
      client
        .get(uri, options)
        .then((res) => {
          resolve(res.data)
        })
        .catch((err) => {
          reject(err)
        })
    })
  },

  updateCommentStatus: (serviceId, commentId, publishStatus, token = null) => {
    return new Promise((resolve, reject) => {
      const vals = { publishStatus }
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/comments/${serviceId}/${commentId}/status`
      console.log('updateCommentStatus', uri, vals)
      client
        .post(uri, vals, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  },

  deleteComment: (serviceId, commentId, token = null) => {
    return new Promise((resolve, reject) => {
      const options = utilUri.getReqOptions(null, token)
      const uri = `admin/comments/${serviceId}/${commentId}`
      client
        .delete(uri, options)
        .then((res) => resolve(res.data))
        .catch((err) => reject(err))
    })
  }
}
