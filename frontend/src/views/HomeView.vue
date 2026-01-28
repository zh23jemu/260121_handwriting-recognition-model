<template>
  <div class="home-container">
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
</template>

<style scoped>
.home-container {
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

.btn-primary {
  background: #2563eb;
  color: white;
}

.btn-primary:hover {
  background: #1d4ed8;
  transform: translateY(-2px);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: white;
  color: #667eea;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover {
  background: #059669;
  transform: translateY(-2px);
}

.home-footer {
  text-align: center;
  padding: 1rem 0;
  background: rgba(0, 0, 0, 0.1);
  opacity: 0.8;
}
</style>