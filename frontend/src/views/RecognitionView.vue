<template>
  <div class="recognition-container">
    <header class="app-header">
      <h1>手写汉字识别</h1>
      <div class="user-info">
        <span>欢迎，{{ username }}</span>
        <router-link v-if="isAdmin" to="/admin" class="btn btn-primary">管理员控制台</router-link>
        <button class="btn btn-secondary" @click="handleLogout">退出登录</button>
      </div>
    </header>
    
    <main class="recognition-main">
      <div class="recognition-section">
        <div class="drawing-area">
          <h2>绘制区域</h2>
          <div class="canvas-container">
            <canvas 
              ref="canvas" 
              width="400" 
              height="400" 
              @mousedown="startDrawing" 
              @mousemove="draw" 
              @mouseup="stopDrawing" 
              @mouseout="stopDrawing"
              @touchstart="handleTouchStart" 
              @touchmove="handleTouchMove" 
              @touchend="handleTouchEnd"
              class="drawing-canvas"
            ></canvas>
          </div>
          <div class="canvas-controls">
            <button class="btn btn-primary" @click="clearCanvas">清空画布</button>
            <button class="btn btn-success" @click="recognizeCharacter" :disabled="isRecognizing">
              {{ isRecognizing ? '识别中...' : '开始识别' }}
            </button>
            <input 
              type="file" 
              accept="image/*" 
              @change="handleImageUpload" 
              class="file-input"
            >
          </div>
        </div>
        
        <div class="result-area">
          <h2>识别结果</h2>
          <div v-if="recognitionResult" class="result-card">
            <div class="main-result">
              <span class="result-label">识别结果：</span>
              <span class="result-char">{{ recognitionResult.result }}</span>
              <span class="result-confidence">({{ (recognitionResult.confidence * 100).toFixed(2) }}%)</span>
            </div>
            <div class="candidates">
              <h3>候选字：</h3>
              <div class="candidate-list">
                <div 
                  v-for="(candidate, index) in recognitionResult.candidates" 
                  :key="index"
                  class="candidate-item"
                >
                  <span class="candidate-char">{{ candidate.char }}</span>
                  <span class="candidate-confidence">({{ (candidate.confidence * 100).toFixed(2) }}%)</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="isRecognizing" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在识别，请稍候...</p>
          </div>
          <div v-else class="empty-result">
            <p>请在左侧绘制汉字，然后点击"开始识别"按钮</p>
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </div>
      </div>
      
      <div class="history-preview">
        <h2>最近识别历史</h2>
        <div class="history-list">
          <div 
            v-for="record in recentHistory" 
            :key="record.id"
            class="history-item"
          >
            <div class="history-char">{{ record.result }}</div>
            <div class="history-info">
              <p>置信度：{{ (record.confidence * 100).toFixed(2) }}%</p>
              <p>{{ formatDate(record.created_at) }}</p>
            </div>
          </div>
        </div>
        <router-link to="/history" class="btn btn-secondary history-btn">查看全部历史</router-link>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RecognitionView',
  data() {
    return {
      username: localStorage.getItem('username') || '用户',
      isAdmin: localStorage.getItem('isAdmin') === 'true',
      isDrawing: false,
      isRecognizing: false,
      recognitionResult: null,
      error: '',
      recentHistory: [],
      ctx: null,
      lastX: 0,
      lastY: 0
    }
  },
  mounted() {
    this.initCanvas()
    this.loadRecentHistory()
  },
  methods: {
    initCanvas() {
      const canvas = this.$refs.canvas
      this.ctx = canvas.getContext('2d')
      this.ctx.lineWidth = 8
      this.ctx.lineCap = 'round'
      this.ctx.lineJoin = 'round'
      this.ctx.strokeStyle = '#000000'
      this.ctx.fillStyle = '#ffffff'
      this.ctx.fillRect(0, 0, canvas.width, canvas.height)
    },
    
    startDrawing(e) {
      this.isDrawing = true
      const pos = this.getMousePos(this.$refs.canvas, e)
      this.lastX = pos.x
      this.lastY = pos.y
    },
    
    draw(e) {
      if (!this.isDrawing) return
      
      const pos = this.getMousePos(this.$refs.canvas, e)
      this.ctx.beginPath()
      this.ctx.moveTo(this.lastX, this.lastY)
      this.ctx.lineTo(pos.x, pos.y)
      this.ctx.stroke()
      
      this.lastX = pos.x
      this.lastY = pos.y
    },
    
    stopDrawing() {
      this.isDrawing = false
    },
    
    getMousePos(canvas, e) {
      const rect = canvas.getBoundingClientRect()
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
      }
    },
    
    handleTouchStart(e) {
      e.preventDefault()
      const touch = e.touches[0]
      const mouseEvent = new MouseEvent('mousedown', {
        clientX: touch.clientX,
        clientY: touch.clientY
      })
      this.$refs.canvas.dispatchEvent(mouseEvent)
    },
    
    handleTouchMove(e) {
      e.preventDefault()
      const touch = e.touches[0]
      const mouseEvent = new MouseEvent('mousemove', {
        clientX: touch.clientX,
        clientY: touch.clientY
      })
      this.$refs.canvas.dispatchEvent(mouseEvent)
    },
    
    handleTouchEnd(e) {
      e.preventDefault()
      const mouseEvent = new MouseEvent('mouseup', {})
      this.$refs.canvas.dispatchEvent(mouseEvent)
    },
    
    clearCanvas() {
      const canvas = this.$refs.canvas
      this.ctx.fillStyle = '#ffffff'
      this.ctx.fillRect(0, 0, canvas.width, canvas.height)
      this.recognitionResult = null
      this.error = ''
    },
    
    handleImageUpload(e) {
      const file = e.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (event) => {
          const img = new Image()
          img.onload = () => {
            const canvas = this.$refs.canvas
            this.ctx.fillStyle = '#ffffff'
            this.ctx.fillRect(0, 0, canvas.width, canvas.height)
            
            // 计算图像缩放比例
            const scale = Math.min(canvas.width / img.width, canvas.height / img.height)
            const x = (canvas.width - img.width * scale) / 2
            const y = (canvas.height - img.height * scale) / 2
            
            this.ctx.drawImage(img, x, y, img.width * scale, img.height * scale)
          }
          img.src = event.target.result
        }
        reader.readAsDataURL(file)
      }
    },
    
    async recognizeCharacter() {
      if (this.isRecognizing) return
      
      this.isRecognizing = true
      this.error = ''
      
      try {
        // 将画布内容转换为Blob
        const canvas = this.$refs.canvas
        const blob = await new Promise((resolve) => {
          canvas.toBlob(resolve, 'image/png')
        })
        
        const formData = new FormData()
        formData.append('image', blob, 'drawing.png')
        
        // 发送识别请求
        const token = localStorage.getItem('token')
        console.log('Token:', token)
        console.log('Sending recognition request...')
        console.log('FormData size:', formData.getAll('image').length)
        
        // 确保token存在
        if (!token) {
          throw new Error('No token found in localStorage')
        }
        
        const response = await axios.post(
          'http://localhost:8000/api/recognition/recognize/',
          formData,
          {
            headers: {
              'Authorization': `Bearer ${token}`
              // 注意：axios会自动为FormData设置正确的Content-Type
            }
          }
        )
        
        console.log('Recognition response:', response.data)
        this.recognitionResult = response.data
        this.loadRecentHistory() // 更新历史记录
      } catch (err) {
        console.error('识别失败:', err)
        console.error('Error details:', err.response)
        this.error = err.response?.data?.error || '识别失败，请重试'
      } finally {
        this.isRecognizing = false
      }
    },
    
    async loadRecentHistory() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/recognition/history/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.recentHistory = response.data.slice(0, 5) // 只显示最近5条记录
      } catch (err) {
        console.error('加载历史记录失败:', err)
      }
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
.recognition-container {
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

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-info span {
  font-weight: bold;
}

.recognition-main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.recognition-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.drawing-area, .result-area {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.drawing-area h2, .result-area h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.canvas-container {
  display: flex;
  justify-content: center;
  margin: 1rem 0;
}

.drawing-canvas {
  border: 2px solid #ddd;
  border-radius: 5px;
  cursor: crosshair;
  background: white;
}

.canvas-controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  font-size: 0.9rem;
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

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-2px);
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #4b5563;
  transform: translateY(-2px);
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.file-input {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  background: white;
  cursor: pointer;
}

.result-card {
  background: #f0f9ff;
  border: 1px solid #3b82f6;
  border-radius: 8px;
  padding: 1.5rem;
  margin-top: 1rem;
}

.main-result {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.result-label {
  font-weight: bold;
  color: #374151;
}

.result-char {
  font-size: 3rem;
  font-weight: bold;
  color: #1e40af;
}

.result-confidence {
  font-size: 1.2rem;
  color: #6b7280;
}

.candidates h3 {
  margin-top: 0;
  color: #374151;
}

.candidate-list {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.candidate-item {
  background: white;
  padding: 0.8rem;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.candidate-char {
  font-size: 2rem;
  font-weight: bold;
  color: #3b82f6;
}

.candidate-confidence {
  font-size: 0.9rem;
  color: #6b7280;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  gap: 1rem;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f4f6;
  border-top: 5px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-result {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
  font-style: italic;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.8rem;
  border-radius: 5px;
  margin-top: 1rem;
  text-align: center;
}

.history-preview {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.history-preview h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.history-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.history-item {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 5px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.history-char {
  font-size: 2rem;
  font-weight: bold;
  color: #667eea;
}

.history-info {
  flex: 1;
}

.history-info p {
  margin: 0.25rem 0;
  font-size: 0.8rem;
  color: #6b7280;
}

.history-btn {
  display: block;
  margin: 1rem auto 0;
  text-align: center;
}

@media (max-width: 768px) {
  .recognition-section {
    grid-template-columns: 1fr;
  }
  
  .app-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
}
</style>