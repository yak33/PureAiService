<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>🤖 AI服务平台</h1>
          <el-menu
            :default-active="$route.path"
            mode="horizontal"
            router
            class="nav-menu"
          >
            <el-menu-item index="/">
              <el-icon><House /></el-icon>
              <span>首页</span>
            </el-menu-item>
            <el-menu-item index="/text">
              <el-icon><Document /></el-icon>
              <span>文本分析</span>
            </el-menu-item>
            <el-menu-item index="/code">
              <el-icon><Cpu /></el-icon>
              <span>代码助手</span>
            </el-menu-item>
            <el-menu-item index="/chat">
              <el-icon><ChatDotRound /></el-icon>
              <span>智能对话</span>
            </el-menu-item>
            <el-menu-item index="/ocr">
              <el-icon><Camera /></el-icon>
              <span>文字识别</span>
            </el-menu-item>
            <el-menu-item index="/image">
              <el-icon><Picture /></el-icon>
              <span>图像描述</span>
            </el-menu-item>
          </el-menu>
        </div>
      </el-header>
      
      <el-main>
        <router-view />
      </el-main>
      
      <el-footer>
        <div class="footer-content">
          <p>© 2024 AI服务平台 - 基于大模型API的纯AI服务</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style scoped>
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-content h1 {
  color: #409EFF;
  margin: 0;
  font-size: 24px;
}

.nav-menu {
  background: transparent;
  border: none;
}

.footer-content {
  text-align: center;
  padding: 20px 0;
  color: #666;
}

.footer-content p {
  margin: 0;
}

#app {
  min-height: 100vh;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.el-main {
  background-color: #f5f5f5;
  min-height: calc(100vh - 120px);
}

.el-footer {
  background-color: #fff;
  border-top: 1px solid #e4e4e4;
}
</style>