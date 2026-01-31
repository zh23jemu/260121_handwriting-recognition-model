<template>
  <div class="recognition-container">
    <!-- 全局导航已在App.vue中添加 -->
    
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
          <!-- 识别结果标题 -->
          <div class="result-header">
            <h2>识别结果</h2>
          </div>
          
          <!-- 识别结果卡片 -->
          <div v-if="recognitionResult" class="result-card">
            <!-- 原始绘制图像 -->
            <div class="original-image-preview">
              <img :src="canvasImage" alt="原始绘制图像" class="original-image">
            </div>
            
            <!-- 识别文字 -->
            <div class="recognized-text-section">
              <h3>识别文字:</h3>
              <div class="recognized-text">
                {{ recognitionResult.result }}
              </div>
            </div>
            
            <!-- 详细信息 -->
            <div class="detailed-info-section">
              <h3>详细信息:</h3>
              <div class="detailed-info">
                <div class="info-item">
                  <span class="info-char">{{ recognitionResult.result }}</span>
                  <span class="info-confidence">{{ (recognitionResult.confidence * 100).toFixed(1) }}%</span>
                </div>
              </div>
            </div>
            
            <!-- 置信度进度条 -->
            <div class="confidence-section">
              <h3>置信度:</h3>
              <div class="confidence-bar-container">
                <div class="confidence-bar" :style="{ width: (recognitionResult.confidence * 100) + '%' }"></div>
              </div>
              <div class="confidence-value">{{ (recognitionResult.confidence * 100).toFixed(1) }}%</div>
            </div>
          </div>
          
          <!-- 加载状态 -->
          <div v-else-if="isRecognizing" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在识别，请稍候...</p>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="empty-result">
            <p>请在左侧绘制汉字，然后点击"开始识别"按钮</p>
          </div>
          
          <!-- 错误信息 -->
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
      preprocessedImage: null,
      canvasImage: null,
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
      this.ctx.lineWidth = 24
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
      this.preprocessedImage = null
      this.canvasImage = null
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
      this.preprocessedImage = null
      
      try {
        // 将画布内容转换为Blob和DataURL
        const canvas = this.$refs.canvas
        
        // 保存画布图像用于显示
        this.canvasImage = canvas.toDataURL('image/png')
        
        // 转换为Blob用于上传
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
        
        // 处理预处理图像
        if (response.data.preprocessed_image) {
          this.preprocessedImage = `data:image/png;base64,${response.data.preprocessed_image}`
        }
        
        this.loadRecentHistory() // 更新历史记录
      } catch (err) {
        console.error('识别失败:', err)
        console.error('Error details:', err.response)
        this.error = err.response?.data?.error || '识别失败，请重试'
      } finally {
        this.isRecognizing = false
      }
    },
    
    copyResult() {
      if (this.recognitionResult) {
        navigator.clipboard.writeText(this.recognitionResult.result)
          .then(() => {
            alert('识别结果已复制到剪贴板')
          })
          .catch(err => {
            console.error('复制失败:', err)
            alert('复制失败，请手动复制')
          })
      }
    },
    
    downloadResult() {
      if (this.recognitionResult && this.canvasImage) {
        // 创建一个包含识别结果的HTML文件
        const htmlContent = `
          <!DOCTYPE html>
          <html lang="zh-CN">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>手写识别结果</title>
            <style>
              body { font-family: Arial, sans-serif; margin: 20px; }
              .result-container { max-width: 500px; margin: 0 auto; }
              .image-container { text-align: center; margin: 20px 0; }
              .image-container img { border: 1px solid #ddd; padding: 10px; }
              .result-section { margin: 20px 0; }
              .result-text { font-size: 24px; font-weight: bold; text-align: center; margin: 10px 0; }
              .confidence-section { margin: 10px 0; }
              .confidence-bar { height: 10px; background-color: #e0e0e0; border-radius: 5px; overflow: hidden; }
              .confidence-fill { height: 100%; background-color: #4a6cf7; }
            </style>
          </head>
          <body>
            <div class="result-container">
              <h1>手写识别结果</h1>
              <div class="image-container">
                <h3>原始绘制</h3>
                <img src="${this.canvasImage}" alt="原始绘制图像">
              </div>
              <div class="result-section">
                <h3>识别文字</h3>
                <div class="result-text">${this.recognitionResult.result}</div>
              </div>
              <div class="confidence-section">
                <h3>置信度</h3>
                <div class="confidence-bar">
                  <div class="confidence-fill" style="width: ${(this.recognitionResult.confidence * 100)}%"></div>
                </div>
                <p>${(this.recognitionResult.confidence * 100).toFixed(1)}%</p>
              </div>
              <div class="info-section">
                <h3>详细信息</h3>
                <p>识别时间: ${new Date().toLocaleString()}</p>
              </div>
            </div>
          </body>
          </html>
        `
        
        // 创建Blob对象
        const blob = new Blob([htmlContent], { type: 'text/html' })
        
        // 创建下载链接
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `handwriting-recognition-${Date.now()}.html`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
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
  width: 100%;
  max-width: none;
  margin: 0;
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

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.result-header h2 {
    margin: 0;
    color: #333;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
}

.result-actions {
    display: none;
}

.btn-icon {
    margin-right: 0.3rem;
}

.result-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.original-image-preview {
    display: flex;
    justify-content: center;
    margin: 1rem 0;
}

.original-image {
    max-width: 200px;
    max-height: 200px;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    background: white;
}

.recognized-text-section {
    margin: 1.5rem 0;
}

.recognized-text-section h3 {
    margin: 0 0 0.5rem;
    color: #374151;
    font-size: 1.1rem;
}

.recognized-text {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 1rem;
    font-size: 1.5rem;
    font-weight: bold;
    text-align: center;
    color: #1e40af;
}

.detailed-info-section {
    margin: 1.5rem 0;
}

.detailed-info-section h3 {
    margin: 0 0 0.5rem;
    color: #374151;
    font-size: 1.1rem;
}

.detailed-info {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    padding: 1rem;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-char {
    font-size: 1.2rem;
    font-weight: bold;
    color: #374151;
}

.info-confidence {
    font-size: 1rem;
    color: #10b981;
    font-weight: bold;
}

.confidence-section {
    margin: 1.5rem 0;
}

.confidence-section h3 {
    margin: 0 0 0.5rem;
    color: #374151;
    font-size: 1.1rem;
}

.confidence-bar-container {
    height: 10px;
    background-color: #e5e7eb;
    border-radius: 5px;
    overflow: hidden;
    margin: 0.5rem 0;
}

.confidence-bar {
    height: 100%;
    background: linear-gradient(90deg, #4a6cf7, #667eea);
    border-radius: 5px;
    transition: width 0.3s ease;
}

.confidence-value {
    text-align: right;
    font-size: 0.9rem;
    color: #6b7280;
    margin: 0.25rem 0 0;
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