<template>
  <div class="user-management-container">
    <header class="app-header">
      <h1>用户管理</h1>
      <div class="header-actions">
        <router-link to="/admin" class="btn btn-secondary">返回控制台</router-link>
        <button class="btn btn-danger" @click="handleLogout">退出登录</button>
      </div>
    </header>
    
    <main class="user-management-main">
      <!-- 操作栏 -->
      <div class="action-bar">
        <h2>用户列表</h2>
        <button class="btn btn-primary" @click="showAddUserForm = true">添加用户</button>
      </div>
      
      <!-- 搜索和筛选 -->
      <div class="filter-section">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索用户名..."
          class="search-input"
        >
        <select v-model="filterStatus" class="filter-select">
          <option value="all">所有状态</option>
          <option value="active">活跃</option>
          <option value="inactive">非活跃</option>
        </select>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <!-- 错误信息 -->
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <!-- 用户列表 -->
      <div v-else class="user-list">
        <table class="user-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>是否管理员</th>
              <th>状态</th>
              <th>注册时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr 
              v-for="user in filteredUsers" 
              :key="user.id"
              :class="{ 'inactive': !user.is_active }"
            >
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>
                <span class="admin-badge" :class="{ 'is-admin': user.is_admin }">
                  {{ user.is_admin ? '是' : '否' }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="{ 'active': user.is_active }">
                  {{ user.is_active ? '活跃' : '非活跃' }}
                </span>
              </td>
              <td>{{ formatDate(user.date_joined) }}</td>
              <td class="action-buttons">
                <button class="btn btn-sm btn-info" @click="editUser(user)">编辑</button>
                <button class="btn btn-sm btn-danger" @click="confirmDelete(user)">删除</button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <!-- 空状态 -->
        <div v-if="filteredUsers.length === 0" class="empty-state">
          <p>没有找到用户</p>
        </div>
      </div>
      
      <!-- 添加用户表单 -->
      <div v-if="showAddUserForm" class="user-form-overlay" @click.self="showAddUserForm = false">
        <div class="user-form-container">
          <h3>添加用户</h3>
          <form @submit.prevent="addUser">
            <div class="form-group">
              <label for="add-username">用户名</label>
              <input 
                type="text" 
                id="add-username" 
                v-model="newUser.username" 
                required
              >
            </div>
            <div class="form-group">
              <label for="add-email">邮箱</label>
              <input 
                type="email" 
                id="add-email" 
                v-model="newUser.email" 
                required
              >
            </div>
            <div class="form-group">
              <label for="add-password">密码</label>
              <input 
                type="password" 
                id="add-password" 
                v-model="newUser.password" 
                required
              >
            </div>
            <div class="form-group checkbox-group">
              <input 
                type="checkbox" 
                id="add-is-admin" 
                v-model="newUser.is_admin"
              >
              <label for="add-is-admin">是否管理员</label>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="showAddUserForm = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="addingUser">
                {{ addingUser ? '添加中...' : '添加' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 编辑用户表单 -->
      <div v-if="showEditUserForm" class="user-form-overlay" @click.self="showEditUserForm = false">
        <div class="user-form-container">
          <h3>编辑用户</h3>
          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label for="edit-username">用户名</label>
              <input 
                type="text" 
                id="edit-username" 
                v-model="editUser.username" 
                required
              >
            </div>
            <div class="form-group">
              <label for="edit-email">邮箱</label>
              <input 
                type="email" 
                id="edit-email" 
                v-model="editUser.email" 
                required
              >
            </div>
            <div class="form-group">
              <label for="edit-password">密码（留空不修改）</label>
              <input 
                type="password" 
                id="edit-password" 
                v-model="editUser.password"
              >
            </div>
            <div class="form-group checkbox-group">
              <input 
                type="checkbox" 
                id="edit-is-admin" 
                v-model="editUser.is_admin"
              >
              <label for="edit-is-admin">是否管理员</label>
            </div>
            <div class="form-group checkbox-group">
              <input 
                type="checkbox" 
                id="edit-is-active" 
                v-model="editUser.is_active"
              >
              <label for="edit-is-active">是否活跃</label>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-secondary" @click="showEditUserForm = false">取消</button>
              <button type="submit" class="btn btn-primary" :disabled="updatingUser">
                {{ updatingUser ? '更新中...' : '更新' }}
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- 删除确认对话框 -->
      <div v-if="showDeleteConfirm" class="confirm-overlay" @click.self="showDeleteConfirm = false">
        <div class="confirm-dialog">
          <h3>确认删除</h3>
          <p>确定要删除用户 <strong>{{ deleteUser?.username }}</strong> 吗？</p>
          <div class="confirm-actions">
            <button class="btn btn-secondary" @click="showDeleteConfirm = false">取消</button>
            <button class="btn btn-danger" @click="deleteUserConfirm" :disabled="deletingUser">
              {{ deletingUser ? '删除中...' : '删除' }}
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'UserManagementView',
  data() {
    return {
      users: [],
      loading: true,
      error: '',
      searchQuery: '',
      filterStatus: 'all',
      showAddUserForm: false,
      showEditUserForm: false,
      showDeleteConfirm: false,
      addingUser: false,
      updatingUser: false,
      deletingUser: false,
      newUser: {
        username: '',
        email: '',
        password: '',
        is_admin: false
      },
      editUser: {
        id: null,
        username: '',
        email: '',
        password: '',
        is_admin: false,
        is_active: true
      },
      deleteUser: null
    }
  },
  computed: {
    filteredUsers() {
      let filtered = this.users
      
      // 搜索筛选
      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(user => 
          user.username.toLowerCase().includes(query) ||
          user.email.toLowerCase().includes(query)
        )
      }
      
      // 状态筛选
      if (this.filterStatus === 'active') {
        filtered = filtered.filter(user => user.is_active)
      } else if (this.filterStatus === 'inactive') {
        filtered = filtered.filter(user => !user.is_active)
      }
      
      return filtered
    }
  },
  mounted() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = ''
      
      try {
        const token = localStorage.getItem('token')
        const response = await axios.get('http://localhost:8000/api/auth/users/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        this.users = response.data
      } catch (err) {
        this.error = err.response?.data?.error || '加载用户失败'
      } finally {
        this.loading = false
      }
    },
    
    async addUser() {
      this.addingUser = true
      
      try {
        const token = localStorage.getItem('token')
        await axios.post('http://localhost:8000/api/auth/users/', this.newUser, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        // 重置表单
        this.newUser = {
          username: '',
          email: '',
          password: '',
          is_admin: false
        }
        this.showAddUserForm = false
        this.loadUsers() // 重新加载用户列表
      } catch (err) {
        alert(err.response?.data?.error || '添加用户失败')
      } finally {
        this.addingUser = false
      }
    },
    
    editUser(user) {
      this.editUser = {
        id: user.id,
        username: user.username,
        email: user.email,
        password: '',
        is_admin: user.is_admin,
        is_active: user.is_active
      }
      this.showEditUserForm = true
    },
    
    async updateUser() {
      this.updatingUser = true
      
      try {
        const token = localStorage.getItem('token')
        // 移除空密码
        const updateData = { ...this.editUser }
        if (!updateData.password) {
          delete updateData.password
        }
        
        await axios.put(`http://localhost:8000/api/auth/users/${this.editUser.id}/`, updateData, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        this.showEditUserForm = false
        this.loadUsers() // 重新加载用户列表
      } catch (err) {
        alert(err.response?.data?.error || '更新用户失败')
      } finally {
        this.updatingUser = false
      }
    },
    
    confirmDelete(user) {
      this.deleteUser = user
      this.showDeleteConfirm = true
    },
    
    async deleteUserConfirm() {
      if (!this.deleteUser) return
      
      this.deletingUser = true
      
      try {
        const token = localStorage.getItem('token')
        await axios.delete(`http://localhost:8000/api/auth/users/${this.deleteUser.id}/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        this.showDeleteConfirm = false
        this.loadUsers() // 重新加载用户列表
      } catch (err) {
        alert(err.response?.data?.error || '删除用户失败')
      } finally {
        this.deletingUser = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    
    handleLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('isAdmin')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.user-management-container {
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

.user-management-main {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.action-bar h2 {
  margin: 0;
  color: #333;
}

.filter-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.search-input, .filter-select {
  padding: 0.6rem 1rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 0.9rem;
}

.search-input {
  flex: 1;
  min-width: 200px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 4rem;
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

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 1rem;
  border-radius: 5px;
  margin-bottom: 1.5rem;
}

.user-list {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th,
.user-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.user-table th {
  background: #f9fafb;
  font-weight: bold;
  color: #374151;
}

.user-table tr:hover {
  background: #f9fafb;
}

.user-table tr.inactive {
  background: #fef2f2;
}

.admin-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.admin-badge.is-admin {
  background: #d1fae5;
  color: #059669;
}

.admin-badge:not(.is-admin) {
  background: #fef3c7;
  color: #d97706;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.active {
  background: #d1fae5;
  color: #059669;
}

.status-badge:not(.active) {
  background: #fee2e2;
  color: #dc2626;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.8rem;
}

.empty-state {
  text-align: center;
  padding: 4rem;
  color: #6b7280;
}

/* 表单样式 */
.user-form-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.user-form-container {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 500px;
}

.user-form-container h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-group input {
  width: auto;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

/* 确认对话框 */
.confirm-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.confirm-dialog {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.confirm-dialog h3 {
  margin-top: 0;
  color: #333;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

/* 按钮样式 */
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

.btn-info {
  background: #3b82f6;
  color: white;
}

.btn-info:hover:not(:disabled) {
  background: #2563eb;
  transform: translateY(-2px);
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-management-main {
    padding: 1rem;
  }
  
  .action-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .user-table {
    font-size: 0.8rem;
  }
  
  .user-table th,
  .user-table td {
    padding: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .btn-sm {
    width: 100%;
  }
}
</style>