<template>
<div>
  <eb-navbar />
  <div class="container">
    <div class="columns is-desktop">
      <main class="section column" id="main-container">
        <router-view></router-view>
      </main>
      <div class="column is-3-desktop is-2-widescreen">
        <eb-side-nav-menu></eb-side-nav-menu>
      </div>
    </div>
  </div>
</div>
</template>

<script>
import EbNavbar from '@/components/organisms/EbNavbar'
import EbSideNavMenu from '@/components/organisms/EbSideNavMenu'

export default {
  components: {
    EbNavbar,
    EbSideNavMenu,
  },

  computed: {
  },

  created() {
  },

  methods: {
  },
}
</script>

<style scoped>
#main-container {
  overflow: hidden;
}
</style>
