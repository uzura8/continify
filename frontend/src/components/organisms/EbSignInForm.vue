<template>
  <div class="ebSignInForm">
    <div class="field">
      <label class="label">{{ $t('common.email') }}</label>
      <p class="control has-icons-left">
        <input
          type="text"
          v-model="email"
          @blur="validate('email')"
          @keyup.native.enter="keyDownEnter($event)"
          class="input"
          :placeholder="$t('common.email')"
          autocomplete="on"
        />
        <span class="icon is-small is-left">
          <i class="fas fa-envelope"></i>
        </span>
      </p>
      <p
        v-if="checkEmpty(errors.email) === false"
        class="help is-danger"
      >
        {{ errors.email[0] }}
      </p>
    </div>

    <div class="field mt-5">
      <label class="label">{{ $t('common.password') }}</label>
      <p class="control has-icons-left has-icons-right">
        <input
          :type="isMaskPassword ? 'password' : 'text'"
          v-model="password"
          @blur="validate('password')"
          @keyup.native.enter="keyDownEnter($event)"
          class="input"
          :placeholder="$t('common.password')"
          autocomplete="on"
        />
        <span class="icon is-small is-left">
          <i class="fas fa-lock"></i>
        </span>
        <span
          class="icon is-small is-right has-text-grey-dark is-clickable"
          @click.native="isMaskPassword = !isMaskPassword"
        >
          <i
            v-if="isMaskPassword"
            class="fas fa-eye-slash"
          ></i>
          <i
            v-else
            class="fas fa-eye"
          ></i>
        </span>
      </p>
      <p
        v-if="checkEmpty(errors.password) === false"
        class="help is-danger"
      >
        {{ errors.password[0] }}
      </p>
    </div>

    <div class="field is-grouped mt-5">
      <div class="control">
        <button
          class="button is-link"
          :disabled="hasErrors"
          @click="signIn"
        >
          {{ $t('common.signIn') }}
        </button>
      </div>
    </div>

    <div
      v-if="!isAdminPath"
      class="field is-grouped"
    >
      <div class="control">
        <button
          class="button"
          @click="signInWithOAuth('google.com')"
        >
          <span class="icon">
            <i class="fab fa-google"></i>
          </span>
          <span>{{ $t('form["Sign In with Google"]') }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import BField from '@/components/molecules/BField'
import str from '@/util/str'
import obj from '@/util/obj'
import { siteMixin } from '@/mixins/site'
import Cognito from '@/cognito'

export default {
  mixins: [siteMixin],

  components: {
    BField
  },

  props: {
    isUseAdmin: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      errors: {},
      email: '',
      password: '',
      isMaskPassword: true,
      cognito: new Cognito()
    }
  },

  computed: {
    hasErrors() {
      let hasError = false
      Object.keys(this.errors).map((field) => {
        if (this.errors[field].length > 0) hasError = true
      })
      return hasError
    },

    isAdminPath() {
      return this.$route.path.startsWith('/admin')
    }
  },

  created() {
    if (this.isAdminPath && this.isAdminUser) {
      this.redirectByQueryForAdmin()
    }
  },

  methods: {
    checkEmpty: obj.isEmpty,
    async signIn() {
      this.validateAll()
      if (this.hasErrors) {
        this.showGlobalMessage(this.$t('msg["Correct inputs"]'))
        return
      }

      if (this.isAdminPath) {
        await this.signInAdmin()
      } else {
        await this.signInUser()
      }
    },

    async signInUser() {
      try {
        const vals = {
          email: this.email,
          password: this.password
        }
        //await this.$store.dispatch('authenticateWithEmailAndPassword', vals)
        await this.$store.dispatch('authenticate', vals)
        const locationTo = this.$route.query.redirect ? String(this.$route.query.redirect) : ''
        if (locationTo) {
          this.$router.push(locationTo)
        } else {
          this.$router.push('/user')
        }
      } catch (err) {
        this.handleApiError(err, this.$t('msg["Sign In failed"]'))
      }
    },

    async signInAdmin() {
      try {
        this.$store.dispatch('setLoading', true)
        const res = await this.cognito.signIn(this.email, this.password)
        this.$emit('email-signin-complete', 'admin')
        this.$store.dispatch('setLoading', false)
        this.redirectByQueryForAdmin()
      } catch (err) {
        this.debugOutput(err)
        this.$store.dispatch('setLoading', false)
        this.handleApiError(err, this.$t('msg["Sign In failed"]'))
      }
    },

    redirectByQueryForAdmin() {
      const redirectTo = this.$route.query.redirect ? this.$route.query.redirect : '/admin'
      this.$router.push(redirectTo)
    },

    async signInWithOAuth(providerName) {
      try {
        await this.$store.dispatch('authenticateWithOAuth', providerName)
        if (!this.checkEmpty(this.$route.query.redirect)) {
          this.$router.push({ path: this.$route.query.redirect })
        } else {
          if (this.isUseAdmin && this.isAdmin) {
            this.$router.push({ name: 'AdminTop' })
          } else {
            this.$router.push({ name: 'UserTop' })
          }
        }
      } catch (err) {
        this.handleApiError(err, this.$t('msg["Sign In failed"]'))
      }
    },

    keyDownEnter(event) {
      if (event.keyCode !== 13) return
      this.signIn()
    },

    setErrors(errors) {
      const keys = Object.keys(this.errors)
      errors.map((err) => {
        const field = err.param
        this.initErrors(field)
        this.errors[field].push(err.msg)
      })
    },

    validateAll() {
      ;['email', 'password'].map((field) => {
        this.validate(field)
      })
    },

    validate(field) {
      const key = 'validate' + str.capitalize(field)
      this[key]()
    },

    validateEmail() {
      this.initError('email')
      if (this.checkEmpty(this.email)) this.errors.email.push(this.$t('msg["Email is required"]'))
      if (!str.checkEmail(this.email)) this.errors.email.push(this.$t('msg["Email is not valid"]'))
    },

    validatePassword() {
      this.initError('password')
      if (this.checkEmpty(this.password)) {
        this.errors.password.push(this.$t('msg["Password is required"]'))
      }
      if (this.password.length < 6) {
        this.errors.password.push(this.$t('msg["Password must be at least 6 characters"]'))
      }
    },

    initError(field) {
      this.errors[field] = []
    },

    initErrors(field) {
      const keys = Object.keys(this.errors)
      if (!this.inArray(field, keys)) {
        this.initError(field)
      }
    },

    throwReject(err) {
      return Promise.reject(err)
    }
  }
}
</script>
