import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 300000, // 300秒（5分钟）超时，支持复杂模型处理
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加 Token
api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.data)
    
    // 添加 Token 到请求头
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.data)
    return response
  },
  (error) => {
    console.error(
      '响应错误:',
      error.response?.status,
      error.response?.data || error.message
    )
    return Promise.reject(error)
  }
)

export const extractData = (response) => response?.data

// AI服务API
export const aiService = {
  // 认证相关
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  logout: () => api.post('/auth/logout'),
  getUserInfo: () => api.get('/auth/me'),
  updateProfile: (data) => api.put('/auth/profile', data),
  
  // 获取模型列表（本地配置）
  getModels: () => api.get('/ai/models'),
  
  // 获取平台模型列表
  getPlatformModels: (params) => api.get('/ai/platform/models', { params }),
  
  // 获取平台用户信息
  getPlatformUserInfo: () => api.get('/ai/platform/user-info'),
  
  // 获取模型配置
  getModelsConfig: () => api.get('/ai/models-config'),
  
  // 保存模型配置
  saveModelsConfig: (models) => api.post('/ai/models-config', models),
  
  // 健康检查
  healthCheck: () => api.get('/ai/health'),
  
  // 文本分析
  analyzeText: (data) => api.post('/ai/text/analyze', data),
  
  // 对话接口
  chat: (data) => api.post('/ai/chat', data),
  
  // 代码助手
  codeAssist: (data) => api.post('/ai/code', data),
  
  // OCR识别
  ocr: (formData) => api.post('/ai/ocr', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  
  // 图像描述生成
  generateImageDescription: (data) => api.post('/ai/image/describe', data),
  
  // 图片编辑
  editImage: (formData) => api.post('/ai/image/edit', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  
  // 快速AI调用
  quickAI: (data) => api.post('/ai/quick', data),
  
  // 批量处理
  batchProcess: (data) => api.post('/ai/batch', data)
}

export default api