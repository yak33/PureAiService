<template>
  <a-layout id="app">
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
      </div>
    </a-layout-header>

    <a-layout-content class="layout-content">
      <router-view />
    </a-layout-content>

    <a-layout-footer class="layout-footer">
      <div class="footer-content">
        <p>© 2024 AI服务平台 - 基于大模型API的纯AI服务</p>
      </div>
    </a-layout-footer>
  </a-layout>
</template>

<script>
import {
  HomeOutlined,
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  CameraOutlined,
  PictureOutlined,
  EditOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'App',
  components: {
    HomeOutlined,
    FileTextOutlined,
    CodeOutlined,
    MessageOutlined,
    CameraOutlined,
    PictureOutlined,
    EditOutlined
  },
  computed: {
    selectedKeys() {
      return [this.$route.path]
    }
  },
  methods: {
    handleMenuClick({ key }) {
      if (key !== this.$route.path) {
        this.$router.push(key)
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

.nav-menu {
  border-bottom: none;
  background: transparent;
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