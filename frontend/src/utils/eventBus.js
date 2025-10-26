/**
 * 事件总线 - 用于组件间通信
 * 简单的发布订阅模式实现
 * @author ZHANGCHAO
 */

class EventBus {
  constructor() {
    // 存储所有事件监听器
    this.events = {}
  }

  /**
   * 订阅事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  on(eventName, callback) {
    if (!this.events[eventName]) {
      this.events[eventName] = []
    }
    this.events[eventName].push(callback)
  }

  /**
   * 取消订阅事件
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数（如果不传，则清除该事件的所有监听器）
   */
  off(eventName, callback) {
    if (!this.events[eventName]) return

    if (!callback) {
      // 如果没有指定回调函数，清除该事件的所有监听器
      delete this.events[eventName]
    } else {
      // 移除指定的回调函数
      this.events[eventName] = this.events[eventName].filter(cb => cb !== callback)
    }
  }

  /**
   * 触发事件
   * @param {string} eventName - 事件名称
   * @param {*} data - 传递的数据
   */
  emit(eventName, data) {
    if (!this.events[eventName]) return

    // 执行所有监听该事件的回调函数
    this.events[eventName].forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`事件 ${eventName} 的回调执行出错:`, error)
      }
    })
  }

  /**
   * 订阅一次性事件（执行一次后自动取消订阅）
   * @param {string} eventName - 事件名称
   * @param {Function} callback - 回调函数
   */
  once(eventName, callback) {
    const onceCallback = (data) => {
      callback(data)
      this.off(eventName, onceCallback)
    }
    this.on(eventName, onceCallback)
  }
}

// 导出全局单例
export default new EventBus()

// 事件名称常量，方便使用和避免拼写错误
export const EVENT_MODELS_UPDATED = 'models:updated'

