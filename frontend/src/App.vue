<template>
  <div class="app-container">
    <!-- 全局导航 -->
    <GlobalNav v-if="isAuthenticated" />
    
    <!-- 路由出口 -->
    <router-view />
  </div>
</template>

<script>
import GlobalNav from './components/GlobalNav.vue'

export default {
  name: 'App',
  components: {
    GlobalNav
  },
  data() {
    return {
      isAuthenticated: false
    }
  },
  mounted() {
    this.checkAuthStatus()
    window.addEventListener('auth-change', this.checkAuthStatus)
  },
  beforeUnmount() {
    window.removeEventListener('auth-change', this.checkAuthStatus)
  },
  methods: {
    checkAuthStatus() {
      this.isAuthenticated = !!localStorage.getItem('token')
    }
  }
}
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f5f5f5;
  color: #333;
  line-height: 1.6;
}

.app-container {
  min-height: 100vh;
}
</style>
