<template>
  <nav class="global-nav">
    <div class="nav-container">
      <div class="nav-left">
        <router-link to="/" class="nav-item">首页</router-link>
        <router-link to="/recognition" class="nav-item">识别</router-link>
        <router-link to="/history" class="nav-item">历史</router-link>
        <router-link to="/admin" v-if="isAdmin" class="nav-item">统计</router-link>
        <router-link to="/profile" class="nav-item">个人中心</router-link>
        <router-link to="/admin" v-if="isAdmin" class="nav-item admin-item">admin</router-link>
      </div>
      <div class="nav-right">
        <button class="nav-btn" @click="handleLogout">退出</button>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'GlobalNav',
  data() {
    return {
      isAdmin: false
    }
  },
  mounted() {
    this.checkAuthStatus()
  },
  methods: {
    checkAuthStatus() {
      this.isAdmin = localStorage.getItem('isAdmin') === 'true'
    },
    handleLogout() {
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('isAdmin')
      
      // 跳转到登录页面
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.global-nav {
  background: #667eea;
  padding: 0.8rem 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 100%;
  margin: 0 2rem;
}

.nav-left {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: 5px;
  font-weight: bold;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.3);
}

.admin-item {
  background: rgba(0, 0, 0, 0.2);
}

.nav-right {
  display: flex;
  align-items: center;
}

.nav-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 1rem;
    margin: 0 1rem;
  }
  
  .nav-left {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .nav-item {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
  
  .nav-btn {
    padding: 0.4rem 0.8rem;
    font-size: 0.8rem;
  }
}
</style>