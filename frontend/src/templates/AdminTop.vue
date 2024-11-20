<template>
  <div>
    <h1 class="title">{{ $t('page.adminTop') }}</h1>
    <p>{{ $t('msg.signInGreeting', { name: adminUserName }) }}</p>

    <div
      v-if="services"
      class="mt-6"
    >
      <div
        v-for="service in services"
        :key="service.serviceId"
        class="box"
      >
        <h3 class="title is-4 is-flex is-align-items-center mb-5">
          <span>{{ service.label }}</span>
          <span class="ml-2 has-text-weight-normal is-size-6">({{ service.serviceId }})</span>
        </h3>
        <div
          v-if="service.functions"
          class="block"
        >
          <ul>
            <li
              v-for="functionKey in service.functions"
              :key="functionKey"
              class="is-size-5 mt-2 is-flex is-align-items-center"
            >
              <RouterLink
                :to="getFunctionUrl(service.serviceId, functionKey)"
                class="is-flex mr-5"
              >
                {{ $t(`page.adminFunctions["${functionKey}"]`) }}
              </RouterLink>
              <RouterLink
                v-if="functionKey === 'comment'"
                :to="`/admin/settings/${service.serviceId}/content`"
                class="is-flex is-size-6"
              >
                {{ $t('page.managementOf', { label: $t('term.contentId') }) }}
              </RouterLink>
            </li>
          </ul>
        </div>
        <div v-else>{{ $t('msg.noData') }}</div>
      </div>
    </div>
  </div>
</template>
<script>
import { Admin } from '@/api'
import { siteMixin } from '@/mixins/site'

export default {
  components: {},

  mixins: [siteMixin],

  data() {
    return {
      services: []
    }
  },

  computed: {},

  async created() {
    await this.fetchServices()
    //if (this.services.length === 1) {
    //  this.$router.push(`/admin/posts/${this.services[0].serviceId}`)
    //}
  },

  methods: {
    async fetchServices(params = {}) {
      const params_copied = { ...params }
      this.$store.dispatch('setLoading', true)
      try {
        const res = await Admin.getAccountServices(params_copied, this.adminUserToken)
        this.services = res
        const serviceIds = res.map((item) => item.serviceId)
        this.$store.dispatch('setAdminUserAllowedServiceIds', serviceIds)
        this.$store.dispatch('setLoading', false)
      } catch (err) {
        console.log(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Failed to get data from server"]'))
      }
    },

    getFunctionUrl(serviceId, functinKey) {
      let path = ''
      switch (functinKey) {
        case 'post':
          path = 'posts'
          break
        case 'comment':
          path = 'comments'
          break
      }
      if (!path) return ''
      return `/admin/${path}/${serviceId}`
    }
  }
}
</script>
