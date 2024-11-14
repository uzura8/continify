<template>
  <nav class="navbar is-dark">
    <div class="navbar-brand">
      <a
        class="navbar-item"
        href=""
      >
        <router-link
          to="/admin"
          class="navbar-item"
        >
          <img
            :src="logoUrl"
            width="112"
            height="28"
          />
        </router-link>
      </a>
      <div
        class="navbar-burger burger"
        v-bind:class="{ 'is-active': isHeaderMenuOpen }"
        @click="toggleHeaderMenuOpen()"
      >
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
    <div
      class="navbar-menu"
      v-bind:class="{ 'is-active': isHeaderMenuOpen }"
    >
      <div class="navbar-start">
        <router-link
          to="/admin"
          class="navbar-item"
          >{{ $t('page.adminTop') }}</router-link
        >
        <router-link
          v-if="hasAdminRole"
          to="/admin/services"
          class="navbar-item"
          >{{ $t('page.ServiceManagement') }}</router-link
        >
        <router-link
          v-if="hasAdminRole"
          to="/admin/users"
          class="navbar-item"
          >{{ $t('page.AdminUserManagement') }}</router-link
        >
        <a
          v-if="isAdminUser"
          class="navbar-item u-clickable"
          @click="signOut"
          >{{ $t('common.signOut') }}</a
        >
      </div>
    </div>
  </nav>
</template>

<script>
import config from '@/config/config'
import listener from '@/listener'
import Cognito from '@/cognito'

export default {
  data() {
    return {
      cognito: new Cognito()
    }
  },

  computed: {
    isHeaderMenuOpen: function () {
      return this.$store.state.common.isHeaderMenuOpen
    },

    logoUrl: function () {
      return config.logoUrls.admin
    },

    isAdminPath: function () {
      return this.$route.path.startsWith('/admin')
    },

    isAdminUser() {
      return this.$store.getters.isAdminUser()
    },

    hasAdminRole() {
      return this.$store.getters.hasAdminRole()
    }
  },

  unmounted: function () {
    this.destroyedComponent()
  },

  methods: {
    destroyedComponent: listener.destroyed,
    toggleHeaderMenuOpen: function () {
      this.$store.dispatch('setHeaderMenuOpen', !this.isHeaderMenuOpen)
    },

    signOut: function () {
      this.cognito.signOut()
      this.$router.push('/admin/signin')
    }
  }
}
</script>
