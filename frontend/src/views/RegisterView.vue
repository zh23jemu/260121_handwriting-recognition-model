<template>
  <div class="register-container">
    <div class="register-form">
      <h2>用户注册</h2>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="formData.username" 
            required 
            placeholder="请输入用户名"
          >
        </div>
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="formData.email" 
            required 
            placeholder="请输入邮箱"
          >
        </div>
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="formData.password" 
            required 
            placeholder="请输入密码"
          >
        </div>
        <div class="form-group">
          <label for="confirm_password">确认密码</label>
          <input 
            type="password" 
            id="confirm_password" 
            v-model="formData.confirm_password" 
            required 
            placeholder="请确认密码"
          >
        </div>
        <div class="form-group">
          <button type="submit" class="btn btn-primary" :disabled="isLoading || formData.password !== formData.confirm_password">
            {{ isLoading ? '注册中...' : '注册' }}
          </button>
        </div>
        <div class="form-footer">
          <p>已有账号？<router-link to="/login">立即登录</router-link></p>
        </div>
      </form>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'RegisterView',
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        confirm_password: ''
      },
      isLoading: false,
      error: ''
    }
  },
  methods: {
    async handleRegister() {
      if (this.formData.password !== this.formData.confirm_password) {
        this.error = '两次输入的密码不一致'
        return
      }
      
      this.isLoading = true
      this.error = ''
      
      try {
        const response = await axios.post('http://localhost:8000/api/auth/register/', {
          username: this.formData.username,
          email: this.formData.email,
          password: this.formData.password
        })
        
        // 注册成功，跳转到登录页面
        this.$router.push('/login')
      } catch (err) {
        // 显示完整的错误信息，方便调试
        console.log('注册失败详情:', err)
        if (err.response?.status === 400) {
          if (typeof err.response.data === 'object') {
            // 处理字段级错误
            const errors = []
            for (const [field, messages] of Object.entries(err.response.data)) {
              errors.push(`${field}: ${Array.isArray(messages) ? messages.join(', ') : messages}`)
            }
            this.error = errors.join('; ')
          } else {
            // 处理非字段级错误
            this.error = err.response.data || '注册失败，请检查输入信息'
          }
        } else {
          this.error = '注册失败，请检查网络连接'
        }
      } finally {
        this.isLoading = false
      }
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
}

.register-form {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.register-form h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
}

.btn {
  width: 100%;
  padding: 0.8rem;
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

.form-footer {
  text-align: center;
  margin-top: 1rem;
}

.form-footer p {
  color: #666;
}

.form-footer a {
  color: #667eea;
  text-decoration: none;
  font-weight: bold;
}

.form-footer a:hover {
  text-decoration: underline;
}

.error-message {
  background: #fee2e2;
  color: #dc2626;
  padding: 0.8rem;
  border-radius: 5px;
  margin-top: 1rem;
  text-align: center;
}
</style>