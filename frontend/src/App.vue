<template>
  <a-layout id="app" v-if="!isLoginPage">
    <a-layout-header class="layout-header">
      <div class="header-content">
        <h1>🤖 AI服务平台</h1>
        <a-menu
          mode="horizontal"
          :selectedKeys="selectedKeys"
          @click="handleMenuClick"
          class="nav-menu"
        >
          <a-menu-item key="/">
            <HomeOutlined />
            <span>首页</span>
          </a-menu-item>
          <a-menu-item key="/text">
            <FileTextOutlined />
            <span>文本分析</span>
          </a-menu-item>
          <a-menu-item key="/code">
            <CodeOutlined />
            <span>代码助手</span>
          </a-menu-item>
          <a-menu-item key="/chat">
            <MessageOutlined />
            <span>智能对话</span>
          </a-menu-item>
          <a-menu-item key="/ocr">
            <CameraOutlined />
            <span>文字识别</span>
          </a-menu-item>
          <a-menu-item key="/image">
            <PictureOutlined />
            <span>图像描述</span>
          </a-menu-item>
          <a-menu-item key="/image-edit">
            <EditOutlined />
            <span>图片编辑</span>
          </a-menu-item>
        </a-menu>
        
        <div class="header-actions">
          <span class="welcome-text">
            👋 欢迎你，
            <a class="nickname-link" @click="showProfileModal = true">{{ nickname }}</a>
          </span>
          <a-button type="link" @click="handleLogout" danger>
            <LogoutOutlined />
            <span>登出</span>
          </a-button>
        </div>
      </div>
    </a-layout-header>

    <a-layout-content class="layout-content">
      <router-view />
    </a-layout-content>

    <a-layout-footer class="layout-footer">
      <div class="footer-content">
        <p>© 2025 AI服务平台 - 基于大模型API的纯AI服务</p>
      </div>
    </a-layout-footer>
  </a-layout>
  
  <!-- 登录页单独显示，不需要导航栏 -->
  <router-view v-else />

  <!-- 修改用户信息弹窗 -->
  <a-modal
    v-model:open="showProfileModal"
    title="修改用户信息"
    :footer="null"
    width="450px"
  >
    <a-form
      :model="profileForm"
      @finish="handleUpdateProfile"
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 18 }"
      label-align="right"
      style="margin-top: 24px;"
    >
      <a-form-item label="用户名">
        <a-input :value="username" disabled />
      </a-form-item>

      <a-form-item
        label="昵称"
        name="nickname"
        :rules="[{ max: 20, message: '昵称长度不能超过20个字符' }]"
      >
        <a-input
          v-model:value="profileForm.nickname"
          placeholder="输入新昵称"
        />
      </a-form-item>

      <a-divider>修改密码</a-divider>

      <a-form-item
        label="旧密码"
        name="old_password"
      >
        <a-input-password
          v-model:value="profileForm.old_password"
          placeholder="输入旧密码"
        />
      </a-form-item>

      <a-form-item
        label="新密码"
        name="new_password"
        :rules="[
          { min: 6, message: '新密码长度至少为6个字符', trigger: 'change' }
        ]"
      >
        <a-input-password
          v-model:value="profileForm.new_password"
          placeholder="输入新密码（至少6个字符）"
        />
      </a-form-item>

      <a-form-item>
        <a-space style="width: 100%; justify-content: flex-end;">
          <a-button @click="showProfileModal = false">取消</a-button>
          <a-button type="primary" html-type="submit" :loading="profileLoading">
            保存
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script>
import { message } from 'ant-design-vue'
import {
  HomeOutlined,
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  CameraOutlined,
  PictureOutlined,
  EditOutlined,
  LogoutOutlined
} from '@ant-design/icons-vue'
import { aiService } from './services/api'

export default {
  name: 'App',
  components: {
    HomeOutlined,
    FileTextOutlined,
    CodeOutlined,
    MessageOutlined,
    CameraOutlined,
    PictureOutlined,
    EditOutlined,
    LogoutOutlined
  },
  data() {
    return {
      username: localStorage.getItem('username') || '用户',
      nickname: localStorage.getItem('nickname') || localStorage.getItem('username') || '用户',
      showProfileModal: false,
      profileForm: {
        nickname: '',
        old_password: '',
        new_password: ''
      },
      profileLoading: false
    }
  },
  computed: {
    selectedKeys() {
      return [this.$route.path]
    },
    isLoginPage() {
      return this.$route.path === '/login'
    }
  },
  watch: {
    showProfileModal(val) {
      if (val) {
        // 打开弹窗时，初始化表单
        this.profileForm.nickname = this.nickname
        this.profileForm.old_password = ''
        this.profileForm.new_password = ''
      }
    }
  },
  methods: {
    handleMenuClick({ key }) {
      if (key !== this.$route.path) {
        this.$router.push(key)
      }
    },
    async handleLogout() {
      try {
        await aiService.logout()
      } catch (error) {
        console.error('登出请求失败:', error)
      } finally {
        // 清除本地存储
        localStorage.removeItem('token')
        localStorage.removeItem('username')
        localStorage.removeItem('nickname')
        
        message.success('已登出')
        
        // 跳转到登录页
        this.$router.push('/login')
      }
    },
    async handleUpdateProfile() {
      this.profileLoading = true
      try {
        const requestData = {}
        
        // 如果昵称有变化，添加到请求
        if (this.profileForm.nickname && this.profileForm.nickname !== this.nickname) {
          requestData.nickname = this.profileForm.nickname
        }
        
        // 如果要修改密码
        if (this.profileForm.new_password) {
          if (!this.profileForm.old_password) {
            message.warning('修改密码需要输入旧密码')
            return
          }
          requestData.old_password = this.profileForm.old_password
          requestData.new_password = this.profileForm.new_password
        }
        
        // 如果没有任何修改
        if (Object.keys(requestData).length === 0) {
          message.warning('没有需要修改的信息')
          return
        }
        
        const response = await aiService.updateProfile(requestData)
        
        message.success('更新成功')
        
        // 更新昵称
        if (response.data.nickname) {
          this.nickname = response.data.nickname
          localStorage.setItem('nickname', response.data.nickname)
        }
        
        // 关闭弹窗
        this.showProfileModal = false
        
        // 如果修改了密码，提示重新登录
        if (requestData.new_password) {
          message.info('密码已修改，请重新登录', 3)
          setTimeout(() => {
            this.handleLogout()
          }, 3000)
        }
        
      } catch (error) {
        console.error('更新用户信息失败:', error)
        message.error(error.response?.data?.detail || '更新失败，请稍后重试')
      } finally {
        this.profileLoading = false
      }
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 0 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  color: #1677ff;
  margin: 0;
  font-size: 24px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-left: 24px;
}

.welcome-text {
  color: #595959;
  font-size: 14px;
}

.nickname-link {
  color: #1677ff;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;
}

.nickname-link:hover {
  color: #4096ff;
  text-decoration: underline;
}

.nav-menu {
  border-bottom: none;
  background: transparent;
  flex: 1;
}

.nav-menu :deep(.ant-menu-item) {
  display: flex;
  align-items: center;
  gap: 6px;
}

.layout-content {
  background-color: #f5f5f5;
  min-height: calc(100vh - 120px);
  padding: 0;
}

.layout-footer {
  background-color: #fff;
  border-top: 1px solid #e4e4e4;
}

.footer-content {
  text-align: center;
  padding: 20px 0;
  color: #666;
}

.footer-content p {
  margin: 0;
}
</style>