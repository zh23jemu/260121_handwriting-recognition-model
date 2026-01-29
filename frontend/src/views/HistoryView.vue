<template>
  <div class="history-container">
    <header class="app-header">
      <h1>识别历史记录</h1>
      <div class="header-actions">
        <router-link v-if="isAdmin" to="/admin" class="btn btn-primary">
          <span class="btn-icon">⚙️</span> 管理员控制台
        </router-link>
        <button class="btn btn-primary" @click="exportHistory">
          <span class="btn-icon">📥</span> 导出CSV
        </button>
        <router-link to="/recognition" class="btn btn-secondary">
          <span class="btn-icon">⬅️</span> 返回识别
        </router-link>
      </div>
    </header>
    
    <main class="history-main">
      <div class="filter-section">
        <div class="search-box">
          <input 
            type="text" 
            placeholder="搜索识别结果..." 
            v-model="searchQuery"
            class="search-input"
          >
        </div>
        <div class="date-filter">
          <label for="start-date">开始日期：</label>
          <input 
            type="date" 
            id="start-date" 
            v-model="startDate"
          >
          <label for="end-date">结束日期：</label>
          <input 
            type="date" 
            id="end-date" 
            v-model="endDate"
          >
        </div>
      </div>
      
      <div class="history-table-container">
        <table class="history-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>识别结果</th>
              <th>置信度</th>
              <th>候选字</th>
              <th>原始图像</th>
              <th>预处理后图像</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="record in filteredHistory" 
              :key="record.id"
              class="history-row"
            >
              <td>{{ record.id }}</td>
              <td class="result-cell">{{ record.result }}</td>
              <td>{{ (record.confidence * 100).toFixed(2) }}%</td>
              <td class="candidates-cell">
                <div class="candidate-badge" 
                     v-for="(candidate, index) in record.candidates" 
                     :key="index">
                  {{ candidate.char }} ({{ (candidate.confidence * 100).toFixed(1) }}%)
                </div>
              </td>
              <td class="image-cell">
                <img 
                  :src="record.image" 
                  :alt="record.result" 
                  class="history-image" 
                  @click="previewImage(record.image)"
                >
              </td>
              <td class="image-cell">
                <img 
                  :src="record.preprocessed_image" 
                  :alt="record.result" 
                  class="history-image" 
                  @click="previewImage(record.preprocessed_image)"
                >
              </td>
              <td>{{ formatDate(record.created_at) }}</td>
              <td class="action-cell">
                <button 
                  class="btn btn-danger btn-small" 
                  @click="deleteRecord(record.id)"
                  :disabled="isDeleting"
                >
                  {{ isDeleting ? '删除中...' : '删除' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="filteredHistory.length === 0" class="empty-state">
          <p>暂无识别历史记录</p>
        </div>
      </div>
      
      <div class="pagination" v-if="filteredHistory.length > 0">
        <button 
          class="btn btn-secondary btn-small" 
          @click="currentPage--" 
          :disabled="currentPage === 1"
        >
          上一页
        </button>
        <span class="page-info">
          第 {{ currentPage }} / {{ totalPages }} 页
        </span>
        <button 
          class="btn btn-secondary btn-small" 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
        >
          下一页
        </button>
      </div>
    </main>
    
    <!-- 图像预览弹窗 -->
    <div v-if="previewImageUrl" class="image-preview-overlay" @click="closePreview">
      <div class="image-preview-container" @click.stop>
        <img :src="previewImageUrl" :alt="'预览图像'" class="preview-image">
        <button class="btn btn-danger btn-close" @click="closePreview">关闭</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'HistoryView',
  data() {
    return {
      historyRecords: [],
      searchQuery: '',
      startDate: '',
      endDate: '',
      currentPage: 1,
      itemsPerPage: 10,
      isLoading: false,
      isDeleting: false,
      previewImageUrl: '',
      error: '',
      isAdmin: localStorage.getItem('isAdmin') === 'true'
    }
  },
  computed: {
    filteredHistory() {
      let filtered = [...this.historyRecords]
      
      // 搜索过滤
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(record => 
          record.result.toLowerCase().includes(query)
        )
      }
      
      // 日期过滤
      if (this.startDate) {
        const start = new Date(this.startDate)
        filtered = filtered.filter(record => 
          new Date(record.created_at) >= start
        )
      }
      
      if (this.endDate) {
        const end = new Date(this.endDate)
        end.setHours(23, 59, 59)
        filtered = filtered.filter(record => 
          new Date(record.created_at) <= end
        )
      }
      
      // 分页
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      return filtered.slice(startIndex, startIndex + this.itemsPerPage)
    },
    totalPages() {
      let filtered = [...this.historyRecords]
      
      // 应用过滤条件
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(record => 
          record.result.toLowerCase().includes(query)
        )
      }
      
      if (this.startDate) {
        const start = new Date(this.startDate)
        filtered = filtered.filter(record => 
          new Date(record.created_at) >= start
        )
      }
      
      if (this.endDate) {
        const end = new Date(this.endDate)
        end.setHours(23, 59, 59)
        filtered = filtered.filter(record => 
          new Date(record.created_at) <= end
        )
      }
      
      return Math.ceil(filtered.length / this.itemsPerPage)
    }
  },
  mounted() {
    this.loadHistory()
  },
  methods: {
    async loadHistory() {
      this.isLoading = true
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/history/', {
          headers: {
            'Authorization': `Token ${token}`
          }
        })
        this.historyRecords = response.data
      } catch (err) {
        this.error = '加载历史记录失败'
        console.error(err)
      } finally {
        this.isLoading = false
      }
    },
    
    async deleteRecord(recordId) {
      if (confirm('确定要删除这条记录吗？')) {
        this.isDeleting = true
        try {
          const token = localStorage.getItem('token')
          await axios.delete(`http://localhost:8000/api/history/${recordId}/`, {
            headers: {
              'Authorization': `Token ${token}`
            }
          })
          // 重新加载历史记录
          this.loadHistory()
        } catch (err) {
          this.error = '删除记录失败'
          console.error(err)
        } finally {
          this.isDeleting = false
        }
      }
    },
    
    async exportHistory() {
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/export/', {
          headers: {
            'Authorization': `Token ${token}`
          },
          responseType: 'blob'
        })
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `recognition_history_${new Date().toISOString().slice(0, 10)}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (err) {
        this.error = '导出历史记录失败'
        console.error(err)
      }
    },
    
    previewImage(imageUrl) {
      this.previewImageUrl = imageUrl
    },
    
    closePreview() {
      this.previewImageUrl = ''
    },
    
    formatDate(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
  }
}
</script>

<style scoped>
.history-container {
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
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
  transform: translateY(-2px);
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-small {
  padding: 0.4rem 0.8rem;
  font-size: 0.8rem;
}

.btn-close {
  margin-top: 1rem;
}

.history-main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-section {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.date-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.date-filter label {
  font-weight: bold;
  color: #555;
}

.date-filter input {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
}

.history-table-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th {
  background: #f8fafc;
  padding: 1rem;
  text-align: left;
  font-weight: bold;
  color: #374151;
  border-bottom: 2px solid #e2e8f0;
}

.history-table td {
  padding: 1rem;
  border-bottom: 1px solid #e2e8f0;
}

.history-row:hover {
  background: #f8fafc;
}

.result-cell {
  font-weight: bold;
  color: #1e40af;
  font-size: 1.2rem;
}

.candidates-cell {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.candidate-badge {
  background: #dbeafe;
  color: #1d4ed8;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: bold;
}

.image-cell {
  width: 80px;
  height: 80px;
  overflow: hidden;
}

.history-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  cursor: pointer;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: transform 0.3s ease;
}

.history-image:hover {
  transform: scale(1.1);
}

.action-cell {
  display: flex;
  gap: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
  font-style: italic;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-info {
  font-weight: bold;
  color: #374151;
}

.image-preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.image-preview-container {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  max-width: 90%;
  max-height: 90%;
  overflow: auto;
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 5px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .app-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .filter-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>