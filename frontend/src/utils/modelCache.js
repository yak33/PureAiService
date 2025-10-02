/**
 * 模型列表缓存工具
 * 用于缓存从后端获取的模型列表,避免频繁请求
 * @author ZHANGCHAO
 */

const CACHE_KEY = 'ai_models_cache'
const CACHE_DURATION = 5 * 60 * 1000 // 5分钟缓存时间

/**
 * 获取缓存的模型列表
 * @returns {Array|null} 如果缓存有效返回模型列表,否则返回null
 */
export function getCachedModels() {
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    if (!cached) return null

    const { models, timestamp } = JSON.parse(cached)
    const now = Date.now()

    // 检查缓存是否过期
    if (now - timestamp > CACHE_DURATION) {
      localStorage.removeItem(CACHE_KEY)
      return null
    }

    return models
  } catch (error) {
    console.error('读取模型缓存失败:', error)
    return null
  }
}

/**
 * 缓存模型列表
 * @param {Array} models - 模型列表
 */
export function setCachedModels(models) {
  try {
    const cacheData = {
      models,
      timestamp: Date.now()
    }
    localStorage.setItem(CACHE_KEY, JSON.stringify(cacheData))
  } catch (error) {
    console.error('保存模型缓存失败:', error)
  }
}

/**
 * 清除模型缓存
 */
export function clearModelsCache() {
  try {
    localStorage.removeItem(CACHE_KEY)
  } catch (error) {
    console.error('清除模型缓存失败:', error)
  }
}
