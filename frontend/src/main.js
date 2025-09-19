import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import Home from './views/Home.vue'
import TextAnalysis from './views/TextAnalysis.vue'
import CodeAssist from './views/CodeAssist.vue'
import Chat from './views/Chat.vue'
import OCR from './views/OCR.vue'
import ImageDescription from './views/ImageDescription.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/text', component: TextAnalysis },
  { path: '/code', component: CodeAssist },
  { path: '/chat', component: Chat },
  { path: '/ocr', component: OCR },
  { path: '/image', component: ImageDescription }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)
app.mount('#app')