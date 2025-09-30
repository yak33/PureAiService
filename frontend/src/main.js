import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import * as AntDesignIconsVue from '@ant-design/icons-vue'

import App from './App.vue'
import Home from './views/Home.vue'
import Login from './views/Login.vue'
import TextAnalysis from './views/TextAnalysis.vue'
import CodeAssist from './views/CodeAssist.vue'
import Chat from './views/Chat.vue'
import OCR from './views/OCR.vue'
import ImageDescription from './views/ImageDescription.vue'
import ImageEdit from './views/ImageEdit.vue'

const routes = [
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/', component: Home },
  { path: '/text', component: TextAnalysis },
  { path: '/code', component: CodeAssist },
  { path: '/chat', component: Chat },
  { path: '/ocr', component: OCR },
  { path: '/image', component: ImageDescription },
  { path: '/image-edit', component: ImageEdit }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 检查登录状态
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 如果是公开页面（登录页），直接放行
  if (to.meta.public) {
    next()
    return
  }
  
  // 如果没有 token，跳转到登录页
  if (!token) {
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
    return
  }
  
  // 已登录，继续访问
  next()
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(AntDesignIconsVue)) {
  app.component(key, component)
}

app.use(Antd)
app.use(router)
app.mount('#app')