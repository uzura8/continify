<template>
  <div>
    <h1 class="title">{{ $t('page.AdminUsers') }}</h1>

    <div class="mt-5">
      <AdminUserList />
    </div>
  </div>
</template>
<script>
import AdminUserList from '@/components/organisms/AdminUserList'

export default {
  components: {
    AdminUserList
  }
}
</script>
