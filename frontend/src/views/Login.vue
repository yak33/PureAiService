<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <Logo size="large" />
        <p>请登录以继续使用服务</p>
      </div>

      <a-form
        :model="form"
        @finish="handleLogin"
        class="login-form"
      >
        <a-form-item
          name="username"
          :rules="[{ required: true, message: '请输入用户名' }]"
        >
          <a-input
            v-model:value="form.username"
            size="large"
            placeholder="用户名"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[{ required: true, message: '请输入密码' }]"
        >
          <a-input-password
            v-model:value="form.password"
            size="large"
            placeholder="密码"
            @keyup.enter="handleLogin"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <!-- 滑动验证码 -->
        <a-form-item>
          <SliderCaptcha ref="captcha" @success="handleCaptchaSuccess" />
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="loading"
            :disabled="!captchaVerified"
          >
            登录
          </a-button>
        </a-form-item>
      </a-form>

      <div class="login-footer">
        <p>
          还没有账号？
          <a @click="showRegisterModal = true">立即注册</a>
        </p>
        <p class="tip">
          <span class="tip-icon">💡</span>
          默认管理员账号: admin / 123456
        </p>
      </div>
    </div>

    <!-- 注册弹窗 -->
    <a-modal
      v-model:open="showRegisterModal"
      title="注册账号"
      :footer="null"
      width="450px"
    >
      <a-form
        :model="registerForm"
        @finish="handleRegister"
        style="margin-top: 24px;"
      >
        <a-form-item
          name="username"
          :rules="[
            { required: true, message: '请输入用户名' },
            { min: 3, max: 20, message: '用户名长度为3-20个字符' }
          ]"
        >
          <a-input
            v-model:value="registerForm.username"
            size="large"
            placeholder="用户名（3-20个字符）"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item name="nickname">
          <a-input
            v-model:value="registerForm.nickname"
            size="large"
            placeholder="昵称（可选，默认使用用户名）"
          >
            <template #prefix>
              <SmileOutlined />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item
          name="password"
          :rules="[
            { required: true, message: '请输入密码' },
            { min: 6, message: '密码长度至少为6个字符' }
          ]"
        >
          <a-input-password
            v-model:value="registerForm.password"
            size="large"
            placeholder="密码（至少6个字符）"
          >
            <template #prefix>
              <LockOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item
          name="confirm_password"
          :rules="[
            { required: true, message: '请确认密码' },
            { validator: validateConfirmPassword }
          ]"
        >
          <a-input-password
            v-model:value="registerForm.confirm_password"
            size="large"
            placeholder="确认密码"
          >
            <template #prefix>
              <SafetyOutlined />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item>
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="registerLoading"
          >
            注册
          </a-button>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { message } from 'ant-design-vue'
import { UserOutlined, LockOutlined, SafetyOutlined, SmileOutlined } from '@ant-design/icons-vue'
import { aiService } from '../services/api'
import SliderCaptcha from '../components/SliderCaptcha.vue'
import Logo from '../components/Logo.vue'

export default {
  name: 'Login',
  components: {
    UserOutlined,
    LockOutlined,
    SafetyOutlined,
    SmileOutlined,
    SliderCaptcha,
    Logo
  },
  data() {
    return {
      form: {
        username: '',
        password: ''
      },
      loading: false,
      captchaVerified: false,
      showRegisterModal: false,
      registerForm: {
        username: '',
        nickname: '',
        password: '',
        confirm_password: ''
      },
      registerLoading: false
    }
  },
  methods: {
    handleCaptchaSuccess() {
      this.captchaVerified = true
      message.success('验证成功')
    },
    async handleLogin() {
      if (!this.form.username || !this.form.password) {
        message.warning('请输入用户名和密码')
        return
      }

      if (!this.captchaVerified) {
        message.warning('请先完成滑动验证')
        return
      }

      this.loading = true
      try {
        const response = await aiService.login({
          username: this.form.username,
          password: this.form.password
        })

        if (response.data.access_token) {
          // 保存 Token 和用户信息
          localStorage.setItem('token', response.data.access_token)
          localStorage.setItem('username', this.form.username)
          localStorage.setItem('nickname', response.data.nickname || this.form.username)
          
          message.success('登录成功！')
          
          // 跳转到首页
          const redirect = this.$route.query.redirect || '/'
          this.$router.push(redirect)
        }
      } catch (error) {
        console.error('登录失败:', error)
        message.error(error.response?.data?.detail || '登录失败，请检查用户名和密码')
        
        // 登录失败，重置验证码
        this.captchaVerified = false
        this.$refs.captcha?.reset()
      } finally {
        this.loading = false
      }
    },
    validateConfirmPassword(rule, value) {
      if (value === '') {
        return Promise.reject('请确认密码')
      } else if (value !== this.registerForm.password) {
        return Promise.reject('两次输入的密码不一致')
      } else {
        return Promise.resolve()
      }
    },
    async handleRegister() {
      this.registerLoading = true
      try {
        const response = await aiService.register({
          username: this.registerForm.username,
          nickname: this.registerForm.nickname,
          password: this.registerForm.password,
          confirm_password: this.registerForm.confirm_password
        })

        message.success('注册成功！')
        
        // 关闭弹窗
        this.showRegisterModal = false
        
        // 清空表单
        this.registerForm = {
          username: '',
          nickname: '',
          password: '',
          confirm_password: ''
        }
        
        // 可选：自动填充到登录表单
        this.form.username = response.data.username
        
      } catch (error) {
        console.error('注册失败:', error)
        message.error(error.response?.data?.detail || '注册失败，请稍后重试')
      } finally {
        this.registerLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
  background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;
}

/* 动态渐变背景动画 */
@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
}

/* 添加漂浮的圆形装饰 */
.login-container::before,
.login-container::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.15;
  animation: float 20s ease-in-out infinite;
}

.login-container::before {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.3);
  top: -150px;
  left: -150px;
  animation: float 20s ease-in-out infinite;
}

.login-container::after {
  width: 400px;
  height: 400px;
  background: rgba(255, 255, 255, 0.2);
  bottom: -200px;
  right: -200px;
  animation: float 25s ease-in-out infinite reverse;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  50% {
    transform: translateY(-30px) rotate(180deg);
  }
}

.login-box {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.1),
    0 0 0 1px rgba(255, 255, 255, 0.3);
  padding: 48px;
  width: 100%;
  max-width: 420px;
  position: relative;
  z-index: 1;
  animation: fadeInUp 0.6s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.login-header p {
  color: #6b7280;
  font-size: 14px;
  margin: 0;
}

.login-form {
  margin-bottom: 16px;
}

.login-footer {
  text-align: center;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.login-footer p {
  color: #6b7280;
  font-size: 14px;
  margin: 8px 0;
}

.login-footer p.tip {
  color: #9ca3af;
  font-size: 12px;
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tip-icon {
  font-size: 14px;
}

.login-footer a {
  color: #667eea;
  cursor: pointer;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}
</style>
