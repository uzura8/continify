<template>
<div>
  <eb-admin-navbar />
  <eb-admin-tab-menu-post v-if="isAdminPostPages" />
  <div class="container" v-cloak>
    <div class="columns is-desktop">
      <main class="section column" id="main-container">
        <router-view></router-view>
      </main>
    </div>
  </div>
</div>
</template>

<script>
import EbAdminNavbar from '@/components/organisms/EbAdminNavbar'
import EbAdminTabMenuPost from '@/components/organisms/EbAdminTabMenuPost'

export default {
  components: {
    EbAdminNavbar,
    EbAdminTabMenuPost,
  },

  computed: {
    isAdminPostPages() {
      if (this.$route.path.startsWith('/admin/posts') === true) return true
      if (this.$route.path.startsWith('/admin/categories') === true) return true
      return false
    },
  },
}
</script>

<style scoped>
#main-container {
  overflow: hidden;
}
</style>
