<template>
  <div class="home-container">
    <!-- 已登录用户的欢迎页面 -->
    <div v-if="isAuthenticated" class="welcome-container">
      <!-- 全局导航已在App.vue中添加 -->
      
      <main class="welcome-main">
        <div class="welcome-section">
          <h2>欢迎回来，{{ username }}</h2>
          <p class="welcome-desc">基于深度学习技术，快速准确地识别手写汉字</p>
        </div>
        
        <div class="stats-cards">
          <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-value">{{ totalRecognition }}</div>
            <div class="stat-label">总识别次数</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📅</div>
            <div class="stat-value">{{ todayRecognition }}</div>
            <div class="stat-label">今日识别</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-value">{{ avgSimilarity }}%</div>
            <div class="stat-label">平均相似度</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon">✅</div>
            <div class="stat-value">{{ successRate }}%</div>
            <div class="stat-label">成功率</div>
          </div>
        </div>
        
        <div class="quick-actions">
          <h3>快捷操作</h3>
          <div class="action-cards">
            <router-link to="/recognition" class="action-card">
              <div class="action-icon">📷</div>
              <h4>开始识别</h4>
              <p>上传手写汉字图片进行识别</p>
            </router-link>
            <router-link to="/history" class="action-card">
              <div class="action-icon">📋</div>
              <h4>识别历史</h4>
              <p>查看和管理历史识别记录</p>
            </router-link>
            <router-link to="/admin" v-if="isAdmin" class="action-card">
              <div class="action-icon">📈</div>
              <h4>数据统计</h4>
              <p>查看识别数据分析报告</p>
            </router-link>
          </div>
        </div>
      </main>
    </div>
    
    <!-- 未登录用户的首页 -->
    <div v-else class="landing-container">
      <header class="home-header">
        <h1>手写汉字识别系统</h1>
        <p>基于深度学习的智能手写汉字识别技术</p>
      </header>
      
      <main class="home-main">
        <div class="features">
          <div class="feature-card">
            <h3>智能识别</h3>
            <p>采用先进的CRNN模型，实现高精度手写汉字识别</p>
          </div>
          <div class="feature-card">
            <h3>实时处理</h3>
            <p>快速图像预处理和模型推理，提供实时识别结果</p>
          </div>
          <div class="feature-card">
            <h3>历史记录</h3>
            <p>保存识别历史，支持随时查看和导出</p>
          </div>
          <div class="feature-card">
            <h3>模型训练</h3>
            <p>管理员可进行模型训练和性能监控</p>
          </div>
        </div>
        
        <div class="action-buttons">
          <router-link to="/login" class="btn btn-primary">登录</router-link>
          <router-link to="/register" class="btn btn-secondary">注册</router-link>
          <router-link to="/recognition" class="btn btn-success">立即体验</router-link>
        </div>
      </main>
      
      <footer class="home-footer">
        <p>&copy; 2024 手写汉字识别系统. All rights reserved.</p>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  data() {
    return {
      isAuthenticated: false,
      isAdmin: false,
      username: '',
      totalRecognition: 1,
      todayRecognition: 1,
      avgSimilarity: '0.0062',
      successRate: 100
    }
  },
  mounted() {
    this.checkAuthStatus()
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
.home-container {
  min-height: 100vh;
  background: #f5f5f5;
}

/* 未登录用户的样式 */
.landing-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.home-header {
  text-align: center;
  padding: 2rem 0;
  background: rgba(0, 0, 0, 0.1);
}

.home-header h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.home-header p {
  font-size: 1.2rem;
  opacity: 0.9;
}

.home-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 3rem;
  width: 100%;
  max-width: 1200px;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.feature-card p {
  opacity: 0.9;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

.home-footer {
  text-align: center;
  padding: 1rem 0;
  background: rgba(0, 0, 0, 0.1);
  opacity: 0.8;
}

/* 已登录用户的欢迎页面样式 */
.welcome-container {
  min-height: 100vh;
  background: #f5f5f5;
  color: #333;
}

.welcome-header {
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

.welcome-main {
  padding: 2rem;
  width: 100%;
  max-width: none;
  margin: 0;
}

.welcome-section {
  margin-bottom: 2rem;
}

.welcome-section h2 {
  margin: 0 0 0.5rem 0;
  font-size: 2rem;
  color: #333;
}

.welcome-desc {
  margin: 0;
  color: #666;
  font-size: 1.1rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 2rem;
  margin-bottom: 1rem;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-size: 0.9rem;
  color: #666;
}

.quick-actions {
  margin-top: 3rem;
}

.quick-actions h3 {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.3rem;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.action-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  text-decoration: none;
  color: #333;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.action-card h4 {
  margin: 0 0 0.5rem 0;
  color: #1e40af;
  font-size: 1.2rem;
}

.action-card p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

/* 按钮样式 */
.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.9rem;
}

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
  transform: translateY(-2px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-header {
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
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .action-cards {
    grid-template-columns: 1fr;
  }
  
  .welcome-main {
    padding: 1rem;
  }
}
</style>