//import SentVerificationMail from '@/templates/SentVerificationMail'
//import RequiredEmailVerification from '@/templates/RequiredEmailVerification'
//import UserVerifyEmail from '@/templates/UserVerifyEmail'
//import UserTop from '@/templates/UserTop'
//import Settings from '@/templates/Settings'
//import PostCategories from '@/templates/PostCategories'
//import PostTags from '@/templates/PostTags'
//import PostGroupItems from '@/templates/PostGroupItems'
//import UserCreate from '@/templates/UserCreate'
//import UserEdit from '@/templates/UserEdit'
//import AdminSignIn from '@/templates/AdminSignIn'

import MainLayout from '@/layouts/MainLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'

export default [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        component: () => import('@/templates/Top')
      },
      //{
      //  path: '/signup',
      //  name: 'SignUp',
      //  component: () => import('@/templates/SignUp')
      //},
      //{
      //  path: '/signup/sent',
      //  name: 'SentVerificationMail',
      //  component: SentVerificationMail
      //},
      {
        path: '/signin',
        name: 'SignIn',
        component: () => import('@/templates/SignIn')
      },
      //{
      //  path: '/errors/required-email-verification',
      //  name: 'RequiredEmailVerification',
      //  component: RequiredEmailVerification
      //},
      //{
      //  path: '/user/verify-email',
      //  name: 'UserVerifyEmail',
      //  component: UserVerifyEmail,
      //  meta: { requiresAuth: true }
      //},
      //{
      //  path: '/user',
      //  name: 'UserTop',
      //  component: UserTop,
      //  meta: { requiresAuth: true }
      //},
      //{
      //  path: '/settings',
      //  name: 'Settings',
      //  component: Settings,
      //  meta: { requiresAuth: true }
      //},
      //{
      //  path: '/posts/:serviceId/categories/:categorySlug?',
      //  name: 'PostCategories',
      //  component: PostCategories,
      //},
      //{
      //  path: '/posts/:serviceId/tags/:tagLabel?',
      //  name: 'PostTags',
      //  component: PostTags,
      //},
      //{
      //  path: '/posts/:serviceId/groups/:slug',
      //  name: 'PostGroupItems',
      //  component: PostGroupItems,
      //},
      {
        path: '/posts/:serviceId/:slug',
        name: 'Post',
        component: () => import('@/templates/Post')
      },
      {
        path: '/posts/:serviceId',
        name: 'Posts',
        component: () => import('@/templates/Posts')
      },
      { path: '/about', component: () => import('@/templates/AboutPage') },
      {
        path: '/error/forbidden',
        name: 'Forbidden',
        component: () => import('@/templates/Forbidden')
      },
      { path: '/error/unauthorized', component: () => import('@/templates/Unauthorized') },
      { path: '/error/notfound', component: () => import('@/templates/NotFound') },
      { path: '/:pathMatch(.*)*', redirect: '/error/notfound' }
    ]
  },
  {
    path: '/admin',
    component: AdminLayout,
    children: [
      {
        path: '/admin/signin',
        name: 'AdminSignIn',
        component: () => import('@/templates/AdminSignIn')
      },
      {
        path: '/admin/services',
        name: 'AdminServices',
        component: () => import('@/templates/AdminServices'),
        meta: {
          requiresAuth: true,
          requiresRoleAdmin: true
        }
      },
      {
        path: '/admin/services/create',
        name: 'AdminServiceCreate',
        component: () => import('@/templates/AdminServiceCreate'),
        meta: {
          requiresAuth: true,
          requiresRoleAdmin: true
        }
      },
      {
        path: '/admin/services/:serviceId/edit',
        name: 'AdminServiceEdit',
        component: () => import('@/templates/AdminServiceEdit'),
        meta: {
          requiresAuth: true,
          requiresRoleAdmin: true
        }
      },
      {
        path: '/admin/users',
        name: 'AdminUsers',
        component: () => import('@/templates/AdminUsers'),
        meta: {
          requiresAuth: true,
          requiresRoleAdmin: true
        }
      },
      {
        path: '/admin/users/:username',
        name: 'AdminUser',
        component: () => import('@/templates/AdminUser'),
        meta: {
          requiresAuth: true,
          requiresRoleAdmin: true
        }
      },
      //{
      //  path: '/admin/users/create',
      //  name: 'AdminUserCreate',
      //  component: UserCreate,
      //  meta: { requiresAuth: true }
      //},
      //{
      //  path: '/admin/users/:uid/edit',
      //  name: 'AdminUserEdit',
      //  component: UserEdit,
      //  meta: { requiresAuth: true }
      //},
      {
        path: '/admin/posts/:serviceId/:postId',
        name: 'AdminPost',
        component: () => import('@/templates/AdminPost'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/:postId/edit',
        name: 'AdminPostEdit',
        component: () => import('@/templates/AdminPostEdit'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/create',
        name: 'AdminPostCreate',
        component: () => import('@/templates/AdminPostCreate'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/groups',
        name: 'AdminPostGroups',
        component: () => import('@/templates/AdminPostGroups'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/groups/create',
        name: 'AdminPostGroupCreate',
        component: () => import('@/templates/AdminPostGroupCreate'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/groups/:slug/edit',
        name: 'AdminPostGroupEdit',
        component: () => import('@/templates/AdminPostGroupEdit'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId/groups/:slug',
        name: 'AdminPostGroup',
        component: () => import('@/templates/AdminPostGroup'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/posts/:serviceId',
        name: 'AdminPosts',
        component: () => import('@/templates/AdminPosts'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/categories/:serviceId',
        name: 'AdminCategories',
        component: () => import('@/templates/AdminCategories'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/categories/:serviceId/create',
        name: 'AdminCategoryCreate',
        component: () => import('@/templates/AdminCategoryCreate'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/categories/:serviceId/:slug/edit',
        name: 'AdminCategoryEdit',
        component: () => import('@/templates/AdminCategoryEdit'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/comments/:serviceId',
        name: 'AdminCommentTopPage',
        component: () => import('@/templates/AdminCommentTopPage'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/comments/:serviceId/content/:contentId',
        name: 'AdminCommentListPage',
        component: () => import('@/templates/AdminCommentListPage'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/settings/:serviceId/content',
        name: 'AdminSettingContentPage',
        component: () => import('@/templates/AdminSettingContentPage'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/shorten-urls/:serviceId/create',
        name: 'AdminShortenUrlCreate',
        component: () => import('@/templates/AdminShortenUrlCreate'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/shorten-urls/:serviceId/:urlId/edit',
        name: 'AdminShortenUrlEdit',
        component: () => import('@/templates/AdminShortenUrlEdit'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/shorten-urls/:serviceId/:urlId',
        name: 'AdminShortenUrl',
        component: () => import('@/templates/AdminShortenUrl'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin/shorten-urls/:serviceId',
        name: 'AdminShortenUrls',
        component: () => import('@/templates/AdminShortenUrls'),
        meta: {
          requiresAuth: true,
          requiresAcceptService: true
        }
      },
      {
        path: '/admin',
        name: 'AdminTop',
        component: () => import('@/templates/AdminTop'),
        meta: { requiresAuth: true }
      },
      {
        path: '/error/forbidden',
        name: 'Forbidden',
        component: () => import('@/templates/Forbidden')
      },
      { path: '/error/unauthorized', component: () => import('@/templates/Unauthorized') },
      { path: '/error/notfound', component: () => import('@/templates/NotFound') },
      { path: '/:pathMatch(.*)*', redirect: '/error/notfound' }
    ]
  }
]
