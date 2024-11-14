<template>
  <div>
    <h1 class="title">{{ $t('common.createOf', { label: $t('term.service') }) }}</h1>
    <AdminServiceForm />
  </div>
</template>
<script>
import AdminServiceForm from '@/components/organisms/AdminServiceForm'

export default {
  components: {
    AdminServiceForm
  }
}
</script>
