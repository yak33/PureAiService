import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url, config.data)
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
  // 获取模型列表
  getModels: () => api.get('/ai/models'),
  
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
  
  // 文档分析
  analyzeDocument: (formData) => api.post('/ai/document/analyze', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  }),
  
  // 图像描述生成
  generateImageDescription: (data) => api.post('/ai/image/describe', data),
  
  // 快速AI调用
  quickAI: (data) => api.post('/ai/quick', data),
  
  // 批量处理
  batchProcess: (data) => api.post('/ai/batch', data)
}

export default api