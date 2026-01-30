<template>
  <div class="profile-container">
    <!-- 已登录用户的个人中心页面 -->
    <div v-if="isAuthenticated" class="profile-main">
      <!-- 全局导航已在App.vue中添加 -->
      
      <main class="profile-content">
        <h2>个人中心</h2>
        
        <div class="profile-grid">
          <!-- 左侧用户信息卡片 -->
          <div class="user-card">
            <div class="avatar">
              <div class="avatar-circle">{{ username.charAt(0).toUpperCase() }}</div>
            </div>
            <div class="user-info">
              <h3>{{ username }}</h3>
              <p class="email">{{ email }}</p>
            </div>
            <div class="user-stats">
              <div class="stat-item">
                <div class="stat-value">{{ totalRecognition }}</div>
                <div class="stat-label">总识别</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ todayRecognition }}</div>
                <div class="stat-label">今日</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ successRate }}%</div>
                <div class="stat-label">成功率</div>
              </div>
            </div>
          </div>
          
          <!-- 右侧表单区域 -->
          <div class="form-section">
            <!-- 个人信息表单 -->
            <div class="form-card">
              <h3>个人信息</h3>
              <form @submit.prevent="handleUpdateProfile">
                <div class="form-group">
                  <label>用户名</label>
                  <input 
                    type="text" 
                    v-model="profileForm.username" 
                    class="form-control"
                  >
                </div>
                <div class="form-group">
                  <label>邮箱</label>
                  <input 
                    type="email" 
                    v-model="profileForm.email" 
                    class="form-control"
                  >
                </div>
                <div class="form-group">
                  <label>注册时间</label>
                  <input 
                    type="text" 
                    v-model="registrationDate" 
                    class="form-control" 
                    disabled
                  >
                </div>
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  {{ isLoading ? '保存中...' : '保存更改' }}
                </button>
              </form>
              <div v-if="message" class="message" :class="messageType">
                {{ message }}
              </div>
            </div>
            
            <!-- 修改密码表单 -->
            <div class="form-card">
              <h3>修改密码</h3>
              <form @submit.prevent="handleChangePassword">
                <div class="form-group">
                  <label>新密码</label>
                  <input 
                    type="password" 
                    v-model="passwordForm.newPassword" 
                    class="form-control"
                    placeholder="请输入新密码"
                  >
                </div>
                <div class="form-group">
                  <label>确认新密码</label>
                  <input 
                    type="password" 
                    v-model="passwordForm.confirmPassword" 
                    class="form-control"
                    placeholder="请确认新密码"
                  >
                </div>
                <button type="submit" class="btn btn-primary" :disabled="isLoading">
                  {{ isLoading ? '修改中...' : '修改密码' }}
                </button>
              </form>
              <div v-if="passwordMessage" class="message" :class="passwordMessageType">
                {{ passwordMessage }}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
    
    <!-- 未登录用户的提示 -->
    <div v-else class="not-authenticated">
      <h2>请先登录</h2>
      <p>您需要登录才能访问个人中心</p>
      <router-link to="/login" class="btn btn-primary">登录</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfileView',
  data() {
    return {
      isAuthenticated: false,
      isAdmin: false,
      username: '',
      email: '',
      totalRecognition: 1,
      todayRecognition: 1,
      successRate: 100,
      registrationDate: '2024-01-01',
      isLoading: false,
      message: '',
      messageType: '',
      passwordMessage: '',
      passwordMessageType: '',
      profileForm: {
        username: '',
        email: ''
      },
      passwordForm: {
        newPassword: '',
        confirmPassword: ''
      }
    }
  },
  mounted() {
    this.checkAuthStatus()
    this.loadUserInfo()
  },
  methods: {
    checkAuthStatus() {
      const token = localStorage.getItem('token')
      const username = localStorage.getItem('username')
      const isAdmin = localStorage.getItem('isAdmin') === 'true'
      
      this.isAuthenticated = !!token
      this.username = username || ''
      this.isAdmin = isAdmin
    },
    loadUserInfo() {
      if (this.isAuthenticated) {
        // 模拟加载用户信息
        this.profileForm.username = this.username
        this.profileForm.email = `${this.username}@qq.com`
        this.email = `${this.username}@qq.com`
      }
    },
    async handleUpdateProfile() {
      this.isLoading = true
      this.message = ''
      
      try {
        // 模拟更新用户信息
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // 更新本地存储中的用户名
        localStorage.setItem('username', this.profileForm.username)
        this.username = this.profileForm.username
        this.email = this.profileForm.email
        
        this.message = '个人信息更新成功'
        this.messageType = 'success'
        
        // 3秒后清除消息
        setTimeout(() => {
          this.message = ''
        }, 3000)
      } catch (error) {
        this.message = '更新失败，请重试'
        this.messageType = 'error'
      } finally {
        this.isLoading = false
      }
    },
    async handleChangePassword() {
      this.isLoading = true
      this.passwordMessage = ''
      
      try {
        // 验证密码
        if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
          throw new Error('两次输入的密码不一致')
        }
        
        if (this.passwordForm.newPassword.length < 6) {
          throw new Error('密码长度至少为6位')
        }
        
        // 模拟修改密码
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        this.passwordMessage = '密码修改成功'
        this.passwordMessageType = 'success'
        
        // 清空密码表单
        this.passwordForm.newPassword = ''
        this.passwordForm.confirmPassword = ''
        
        // 3秒后清除消息
        setTimeout(() => {
          this.passwordMessage = ''
        }, 3000)
      } catch (error) {
        this.passwordMessage = error.message || '修改失败，请重试'
        this.passwordMessageType = 'error'
      } finally {
        this.isLoading = false
      }
    },
    handleLogout() {
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('isAdmin')
      
      // 刷新页面状态
      this.isAuthenticated = false
      this.username = ''
      this.isAdmin = false
      
      // 跳转到登录页面
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.profile-main {
  min-height: 100vh;
  background: #f5f5f5;
  color: #333;
}

.profile-header {
  background: #667eea;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0;
  font-size: 1.8rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.main-nav {
  display: flex;
  gap: 1rem;
}

.nav-item {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 5px;
  transition: all 0.3s ease;
  font-weight: bold;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}

.nav-item.active {
  background: rgba(255, 255, 255, 0.3);
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.username {
  font-weight: bold;
  font-size: 1rem;
}

.profile-content {
  padding: 2rem;
  width: 100%;
  max-width: none;
  margin: 0;
}

.profile-content h2 {
  margin-bottom: 2rem;
  color: #333;
}

.profile-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 2rem;
}

.user-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.avatar {
  margin-bottom: 1.5rem;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: #667eea;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
  margin: 0 auto;
}

.user-info h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
}

.email {
  margin: 0 0 2rem 0;
  color: #666;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e5e7eb;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
  margin-top: 0.25rem;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-card h3 {
  margin: 0 0 1.5rem 0;
  color: #333;
  font-size: 1.2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-weight: 500;
}

.form-control {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.form-control:disabled {
  background: #f9fafb;
  cursor: not-allowed;
}

.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-2px);
}

.message {
  margin-top: 1rem;
  padding: 0.8rem;
  border-radius: 5px;
  font-size: 0.9rem;
}

.message.success {
  background: #d1fae5;
  color: #065f46;
  border: 1px solid #a7f3d0;
}

.message.error {
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.not-authenticated {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  text-align: center;
  padding: 2rem;
}

.not-authenticated h2 {
  margin-bottom: 1rem;
  color: #333;
}

.not-authenticated p {
  margin-bottom: 2rem;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
    padding: 1rem;
  }
  
  .header-right {
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }
  
  .main-nav {
    width: 100%;
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .user-profile {
    width: 100%;
    justify-content: center;
  }
  
  .profile-grid {
    grid-template-columns: 1fr;
  }
  
  .user-card {
    order: -1;
  }
  
  .profile-content {
    padding: 1rem;
  }
}
</style>