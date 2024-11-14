<template>
  <div v-cloak>
    <BLoading
      :active="isLoading"
      :is-full-page="true"
    />
    <router-view />
  </div>
</template>

<script>
//import config from '@/config/config'
import BLoading from '@/components/molecules/BLoading'

export default {
  components: {
    BLoading
  },

  //metaInfo() {
  //  return {
  //    titleTemplate(titleChunk) {
  //      return titleChunk ? `${titleChunk} | ${config.siteName}` : config.siteName
  //    },
  //  }
  //},

  computed: {
    isLoading: function () {
      return this.$store.getters.isLoading()
    }
  },

  created() {},

  methods: {}
}
</script>
