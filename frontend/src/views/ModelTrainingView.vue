<template>
  <div class="model-training-container">
    <header class="app-header">
      <h1>模型训练管理</h1>
      <div class="header-actions">
        <router-link to="/admin" class="btn btn-secondary">返回控制台</router-link>
        <button class="btn btn-danger" @click="handleLogout">退出登录</button>
      </div>
    </header>
    
    <main class="model-training-main">
      <div class="model-selector">
        <h2>选择模型类型</h2>
        <div class="model-options">
          <label class="model-option">
            <input type="radio" v-model="selectedModel" value="crnn">
            <span class="model-name">CRNN模型</span>
          </label>
          <label class="model-option">
            <input type="radio" v-model="selectedModel" value="cnn_mlp">
            <span class="model-name">CNN+MLP模型</span>
          </label>
        </div>
      </div>
      
      <div class="training-params">
        <h2>训练参数设置</h2>
        <div class="params-grid">
          <div class="param-item">
            <label for="epochs">训练轮数 (Epochs):</label>
            <input type="number" id="epochs" v-model.number="trainingParams.epochs" min="1" max="100">
          </div>
          <div class="param-item">
            <label for="batch-size">批次大小 (Batch Size):</label>
            <input type="number" id="batch-size" v-model.number="trainingParams.batchSize" min="1" max="256">
          </div>
          <div class="param-item">
            <label for="learning-rate">学习率 (Learning Rate):</label>
            <input type="number" id="learning-rate" v-model.number="trainingParams.learningRate" step="0.0001" min="0.0001" max="0.1">
          </div>
          <div class="param-item">
            <label for="train-dir">训练数据目录:</label>
            <input type="text" id="train-dir" v-model="trainingParams.trainDir">
          </div>
          <div class="param-item">
            <label for="test-dir">测试数据目录:</label>
            <input type="text" id="test-dir" v-model="trainingParams.testDir">
          </div>
        </div>
      </div>
      
      <div class="training-controls">
        <button class="btn btn-primary" @click="startTraining" :disabled="isTraining">
          {{ isTraining ? '训练中...' : '开始训练' }}
        </button>
        <button class="btn btn-secondary" @click="stopTraining" :disabled="!isTraining">
          停止训练
        </button>
        <button class="btn btn-success" @click="evaluateModel" :disabled="isEvaluating">
          {{ isEvaluating ? '评估中...' : '评估模型' }}
        </button>
        <button class="btn btn-info" @click="compareModels">
          对比模型
        </button>
      </div>
      
      <div class="training-status" v-if="isTraining">
        <h2>训练状态</h2>
        <div class="status-info">
          <div class="status-item">
            <span class="status-label">当前轮次:</span>
            <span class="status-value">{{ currentEpoch }} / {{ trainingParams.epochs }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">训练损失:</span>
            <span class="status-value">{{ currentLoss.toFixed(4) }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">训练准确率:</span>
            <span class="status-value">{{ (currentAccuracy * 100).toFixed(2) }}%</span>
          </div>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
        </div>
        <div class="training-logs">
          <h3>训练日志</h3>
          <div class="logs-container">
            <div v-for="(log, index) in trainingLogs" :key="index" class="log-item">
              {{ log }}
            </div>
          </div>
        </div>
      </div>
      
      <div class="model-performance" v-if="performanceResults.length > 0">
        <h2>模型性能对比</h2>
        <div class="performance-cards">
          <div 
            v-for="result in performanceResults" 
            :key="result.modelType"
            class="performance-card"
          >
            <h3>{{ result.modelType === 'crnn' ? 'CRNN模型' : 'CNN+MLP模型' }}</h3>
            <div class="performance-metrics">
              <div class="metric-item">
                <span class="metric-label">准确率:</span>
                <span class="metric-value">{{ (result.accuracy * 100).toFixed(2) }}%</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">损失值:</span>
                <span class="metric-value">{{ result.loss.toFixed(4) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">训练时间:</span>
                <span class="metric-value">{{ result.trainingTime }}秒</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">参数量:</span>
                <span class="metric-value">{{ result.params }}万</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="visualization">
          <h3>性能可视化</h3>
          <div class="chart-container">
            <!-- 这里可以集成图表库，如Chart.js或ECharts -->
            <div class="placeholder-chart">
              <p>模型性能对比图表</p>
              <div class="chart-simulation">
                <div class="chart-bar" style="height: 85%; background: #3b82f6;">CRNN: 85%</div>
                <div class="chart-bar" style="height: 78%; background: #10b981;">CNN+MLP: 78%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="model-list">
        <h2>已训练模型列表</h2>
        <div class="models-table-container">
          <table class="models-table">
            <thead>
              <tr>
                <th>模型名称</th>
                <th>模型类型</th>
                <th>准确率</th>
                <th>训练时间</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr 
                v-for="model in trainedModels" 
                :key="model.id"
                class="model-row"
              >
                <td>{{ model.name }}</td>
                <td>{{ model.type === 'crnn' ? 'CRNN' : 'CNN+MLP' }}</td>
                <td>{{ (model.accuracy * 100).toFixed(2) }}%</td>
                <td>{{ model.trainingTime }}秒</td>
                <td>{{ formatDate(model.createdAt) }}</td>
                <td class="model-actions">
                  <button class="btn btn-small btn-primary">部署</button>
                  <button class="btn btn-small btn-secondary">查看详情</button>
                  <button class="btn btn-small btn-danger">删除</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="trainedModels.length === 0" class="empty-models">
          <p>暂无已训练的模型</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'ModelTrainingView',
  data() {
    return {
      selectedModel: 'crnn',
      trainingParams: {
        epochs: 10,
        batchSize: 32,
        learningRate: 0.001,
        trainDir: '../../data/train',
        testDir: '../../data/test'
      },
      isTraining: false,
      isEvaluating: false,
      currentEpoch: 0,
      currentLoss: 0,
      currentAccuracy: 0,
      progress: 0,
      trainingLogs: [],
      performanceResults: [
        {
          modelType: 'crnn',
          accuracy: 0.8523,
          loss: 0.4567,
          trainingTime: 1250,
          params: 12.5
        },
        {
          modelType: 'cnn_mlp',
          accuracy: 0.7856,
          loss: 0.6789,
          trainingTime: 890,
          params: 8.3
        }
      ],
      trainedModels: [
        {
          id: 1,
          name: 'crnn_final',
          type: 'crnn',
          accuracy: 0.8523,
          trainingTime: 1250,
          createdAt: '2026-01-22T14:30:00'
        },
        {
          id: 2,
          name: 'cnn_mlp_final',
          type: 'cnn_mlp',
          accuracy: 0.7856,
          trainingTime: 890,
          createdAt: '2026-01-22T16:45:00'
        }
      ]
    }
  },
  methods: {
    async startTraining() {
      this.isTraining = true
      this.currentEpoch = 0
      this.progress = 0
      this.trainingLogs = []
      
      try {
        // 模拟训练过程
        for (let i = 0; i < this.trainingParams.epochs; i++) {
          this.currentEpoch = i + 1
          this.trainingLogs.push(`开始第 ${this.currentEpoch} 轮训练...`)
          
          // 模拟训练耗时
          await this.sleep(1000)
          
          // 模拟训练结果
          this.currentLoss = Math.random() * 0.3 + 0.1
          this.currentAccuracy = Math.random() * 0.1 + 0.8
          this.progress = (this.currentEpoch / this.trainingParams.epochs) * 100
          
          this.trainingLogs.push(`第 ${this.currentEpoch} 轮训练完成 - 损失: ${this.currentLoss.toFixed(4)}, 准确率: ${(this.currentAccuracy * 100).toFixed(2)}%`)
        }
        
        this.trainingLogs.push('训练完成！')
      } catch (err) {
        this.trainingLogs.push(`训练出错: ${err.message}`)
      } finally {
        this.isTraining = false
      }
    },
    
    stopTraining() {
      this.isTraining = false
      this.trainingLogs.push('训练已停止')
    },
    
    async evaluateModel() {
      this.isEvaluating = true
      try {
        this.trainingLogs.push('开始模型评估...')
        await this.sleep(2000)
        this.trainingLogs.push('模型评估完成！')
      } catch (err) {
        this.trainingLogs.push(`评估出错: ${err.message}`)
      } finally {
        this.isEvaluating = false
      }
    },
    
    compareModels() {
      // 模拟模型对比
      this.trainingLogs.push('开始模型对比...')
      setTimeout(() => {
        this.trainingLogs.push('模型对比完成！')
      }, 1500)
    },
    
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms))
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
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
.model-training-container {
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

.btn-primary {
  background: #667eea;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn-success {
  background: #10b981;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
}

.btn-danger {
  background: #ef4444;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-2px);
}

.btn-info {
  background: #3b82f6;
}

.btn-info:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
}

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.model-training-main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.model-selector, .training-params, .training-controls, .training-status, .model-performance, .model-list {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.model-selector h2, .training-params h2, .training-status h2, .model-performance h2, .model-list h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.model-options {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
}

.model-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
  cursor: pointer;
}

.model-option input[type="radio"] {
  width: 18px;
  height: 18px;
}

.model-name {
  font-weight: bold;
  color: #374151;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.param-item label {
  font-weight: bold;
  color: #555;
}

.param-item input {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.param-item input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.training-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.training-status h3, .model-performance h3 {
  margin: 1rem 0 0.5rem 0;
  color: #374151;
}

.status-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem;
  background: #f0f9ff;
  border-radius: 5px;
}

.status-label {
  font-weight: bold;
  color: #374151;
}

.status-value {
  font-weight: bold;
  color: #1e40af;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background: #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.training-logs {
  margin-top: 1rem;
}

.logs-container {
  max-height: 200px;
  overflow-y: auto;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  padding: 1rem;
  font-family: monospace;
  font-size: 0.9rem;
}

.log-item {
  margin-bottom: 0.5rem;
  padding-left: 1rem;
  border-left: 3px solid #3b82f6;
}

.performance-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.performance-card {
  background: #f0f9ff;
  padding: 1.5rem;
  border-radius: 8px;
  border: 1px solid #3b82f6;
}

.performance-card h3 {
  margin: 0 0 1rem 0;
  color: #1e40af;
  text-align: center;
}

.performance-metrics {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.8rem;
  background: white;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-weight: bold;
  color: #374151;
}

.metric-value {
  font-weight: bold;
  color: #1e40af;
  font-size: 1.1rem;
}

.visualization {
  margin-top: 2rem;
}

.chart-container {
  height: 300px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 1rem;
}

.placeholder-chart {
  text-align: center;
}

.placeholder-chart p {
  margin: 0 0 1rem 0;
  color: #6b7280;
  font-weight: bold;
}

.chart-simulation {
  display: flex;
  gap: 2rem;
  align-items: flex-end;
  justify-content: center;
  height: 200px;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  background: linear-gradient(to top, #e5e7eb 1px, transparent 1px);
  background-size: 100% 20px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.chart-bar {
  width: 80px;
  border-radius: 5px 5px 0 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 5px;
  color: white;
  font-weight: bold;
  font-size: 0.8rem;
  transition: height 0.3s ease;
}

.models-table-container {
  overflow-x: auto;
  margin-top: 1rem;
}

.models-table {
  width: 100%;
  border-collapse: collapse;
}

.models-table th, .models-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.models-table th {
  background: #f8fafc;
  font-weight: bold;
  color: #374151;
}

.model-row:hover {
  background: #f8fafc;
}

.model-actions {
  display: flex;
  gap: 0.5rem;
}

.empty-models {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-style: italic;
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
  
  .training-controls {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
  }
}
</style>