<template>
  <div class="admin-container">
    <header class="app-header">
      <h1>管理员控制台</h1>
      <div class="header-actions">
        <router-link to="/recognition" class="btn btn-secondary">返回识别</router-link>
        <button class="btn btn-danger" @click="handleLogout">退出登录</button>
      </div>
    </header>
    
    <main class="admin-main">
      <div class="admin-dashboard">
        <h2>系统概览</h2>
        <div class="stats-cards">
          <div class="stat-card">
            <h3>用户总数</h3>
            <div class="stat-value">{{ userCount }}</div>
          </div>
          <div class="stat-card">
            <h3>识别记录数</h3>
            <div class="stat-value">{{ recordCount }}</div>
          </div>
          <div class="stat-card">
            <h3>今日识别数</h3>
            <div class="stat-value">{{ todayRecords }}</div>
          </div>
          <div class="stat-card">
            <h3>平均准确率</h3>
            <div class="stat-value">{{ avgAccuracy }}%</div>
          </div>
        </div>
      </div>
      
      <div class="admin-actions">
        <h2>管理操作</h2>
        <div class="action-cards">
          <router-link to="/model-training" class="action-card">
            <div class="action-icon">🤖</div>
            <h3>模型训练</h3>
            <p>训练和评估模型性能</p>
          </router-link>
          <router-link to="/user-management" class="action-card">
            <div class="action-icon">👥</div>
            <h3>用户管理</h3>
            <p>管理系统用户</p>
          </router-link>
          <div class="action-card">
            <div class="action-icon">📊</div>
            <h3>系统统计</h3>
            <p>查看系统运行统计</p>
          </div>
          <div class="action-card">
            <div class="action-icon">⚙️</div>
            <h3>系统设置</h3>
            <p>配置系统参数</p>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AdminView',
  data() {
    return {
      userCount: 0,
      recordCount: 0,
      todayRecords: 0,
      avgAccuracy: 0
    }
  },
  mounted() {
    this.loadSystemStats()
  },
  methods: {
    loadSystemStats() {
      // 加载真实系统统计数据
      // 暂时保持为空，后续可添加API调用
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
.admin-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.app-header {
  background: #667eea;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0;
  font-size: 1.8rem;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  color: white;
}

.btn-secondary {
  background: #6b7280;
}

.btn-secondary:hover {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn-danger {
  background: #ef4444;
}

.btn-danger:hover {
  background: #dc2626;
  transform: translateY(-2px);
}

.admin-main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.admin-dashboard, .admin-actions {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.admin-dashboard h2, .admin-actions h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.stat-card {
  background: #f0f9ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #3b82f6;
  text-align: center;
}

.stat-card h3 {
  margin: 0 0 0.5rem 0;
  color: #374151;
  font-size: 1rem;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #1e40af;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.action-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid #e5e7eb;
  text-decoration: none;
  color: #333;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.action-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  margin: 0 0 0.5rem 0;
  color: #1e40af;
}

.action-card p {
  margin: 0;
  color: #6b7280;
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .header-actions {
    width: 100%;
    justify-content: center;
  }
}
</style>