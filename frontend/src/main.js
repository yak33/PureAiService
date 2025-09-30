import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import * as AntDesignIconsVue from '@ant-design/icons-vue'

import App from './App.vue'
import Home from './views/Home.vue'
import TextAnalysis from './views/TextAnalysis.vue'
import CodeAssist from './views/CodeAssist.vue'
import Chat from './views/Chat.vue'
import OCR from './views/OCR.vue'
import ImageDescription from './views/ImageDescription.vue'
import ImageEdit from './views/ImageEdit.vue'

const routes = [
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

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(AntDesignIconsVue)) {
  app.component(key, component)
}

app.use(Antd)
app.use(router)
app.mount('#app')