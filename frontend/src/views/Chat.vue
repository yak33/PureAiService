<template>
  <div class="chat">
    <a-card class="chat-card">
      <template #title>
        <div class="card-header">
          <span>💬 智能对话</span>
          <div class="header-controls">
            <a-select v-model:value="currentModel" size="small" style="width: 240px" placeholder="选择AI模型"
              :loading="loadingModels" show-search :filter-option="filterOption">
              <a-select-option v-for="model in availableModels" :key="model.id" :value="model.id">
                {{ model.id }}
              </a-select-option>
            </a-select>
            <a-tooltip title="如果没有可用模型，请先在模型管理页面配置">
              <a-button size="small" type="link" v-if="!loadingModels && availableModels.length === 0" danger>
                ⚠️ 无可用模型
              </a-button>
            </a-tooltip>
            <a-button size="small" @click="clearChat">
              <DeleteOutlined />
              <span>清空对话</span>
            </a-button>
          </div>
        </div>
      </template>

      <div class="chat-container">
        <div class="messages-container" ref="messagesContainer">
          <div v-for="(message, index) in messages" :key="index"
            :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']">
            <div class="message-avatar">
              <UserOutlined v-if="message.role === 'user'" />
              <RobotOutlined v-else />
            </div>
            <div class="message-content">
              <div class="message-text" v-html="renderMarkdown(message.content)"></div>
              <div class="message-time">
                {{ formatTime(message.timestamp) }}
              </div>
            </div>
            <div class="message-actions" v-if="message.role === 'assistant'">
              <a-button type="link" size="small" @click="copyMessage(message.content)">
                <CopyOutlined />
              </a-button>
            </div>
          </div>

          <div v-if="loading" class="message assistant-message">
            <div class="message-avatar">
              <RobotOutlined />
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <div class="input-container">
          <a-collapse v-model:activeKey="showAdvanced" class="advanced-settings">
            <a-collapse-panel key="1">
              <template #header>
                <div class="collapse-header">
                  <SettingOutlined />
                  <span>高级设置</span>
                </div>
              </template>

              <a-form :model="settings" layout="vertical" size="small">
                <a-form-item label="系统提示词">
                  <a-textarea v-model:value="settings.systemPrompt" :rows="2" placeholder="可选：设置AI的角色和行为..."
                    :auto-size="{ minRows: 2, maxRows: 6 }" />
                </a-form-item>
                <a-form-item label="温度参数">
                  <div class="slider-wrapper">
                    <a-slider v-model:value="settings.temperature" :min="0" :max="1" :step="0.1" />
                    <span class="slider-label">{{ settings.temperature }} ({{ getTemperatureLabel() }})</span>
                  </div>
                </a-form-item>
                <a-form-item label="最大Token">
                  <a-input-number v-model:value="settings.maxTokens" :min="100" :max="4000" :step="100" />
                </a-form-item>
              </a-form>
            </a-collapse-panel>
          </a-collapse>

          <div class="input-area">
            <a-textarea v-model:value="inputMessage" :rows="3" placeholder="输入您的问题..."
              :auto-size="{ minRows: 3, maxRows: 6 }" @keydown.ctrl.enter="sendMessage" :disabled="loading" />
            <div class="input-actions">
              <a-button type="primary" @click="sendMessage" :loading="loading" :disabled="!inputMessage.trim()">
                <SendOutlined />
                <span>发送 (Ctrl+Enter)</span>
              </a-button>
            </div>
          </div>
        </div>
      </div>
    </a-card>
  </div>
</template>

<script>
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import {
  DeleteOutlined,
  CopyOutlined,
  UserOutlined,
  RobotOutlined,
  SendOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'
import { getCachedModels, setCachedModels } from '../utils/modelCache'
import eventBus, { EVENT_MODELS_UPDATED } from '../utils/eventBus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

export default {
  name: 'Chat',
  components: {
    DeleteOutlined,
    CopyOutlined,
    UserOutlined,
    RobotOutlined,
    SendOutlined,
    SettingOutlined
  },
  data() {
    return {
      messages: [],
      inputMessage: '',
      loading: false,
      loadingModels: false,
      availableModels: [],
      currentModel: '',
      showAdvanced: [],
      settings: {
        systemPrompt: '',
        temperature: 0.7,
        maxTokens: 2000
      }
    }
  },
  async mounted() {
    await this.loadAvailableModels()
    this.loadChatHistory()

    // 监听模型更新事件
    eventBus.on(EVENT_MODELS_UPDATED, this.handleModelsUpdated)
  },
  beforeUnmount() {
    // 移除事件监听，避免内存泄漏
    eventBus.off(EVENT_MODELS_UPDATED, this.handleModelsUpdated)
  },
  methods: {
    async loadAvailableModels() {
      // 先尝试从缓存读取
      const cachedModels = getCachedModels()
      if (cachedModels && cachedModels.length > 0) {
        this.availableModels = cachedModels
        if (!this.currentModel) {
          const glmModel = this.availableModels.find(m =>
            m.id.includes('GLM-4') && !m.id.includes('V') && !m.id.includes('Vision')
          )
          this.currentModel = glmModel ? glmModel.id : this.availableModels[0].id
        }
        return
      }

      // 缓存不存在或过期，从后端加载
      this.loadingModels = true
      try {
        const response = await aiService.getModels()
        if (response.data.models && response.data.models.length > 0) {
          this.availableModels = response.data.models
          // 保存到缓存
          setCachedModels(this.availableModels)
          // 优先选择GLM-4.5（非视觉模型），如果不存在则选择第一个
          if (!this.currentModel && this.availableModels.length > 0) {
            const glmModel = this.availableModels.find(m =>
              m.id.includes('GLM-4') && !m.id.includes('V') && !m.id.includes('Vision')
            )
            this.currentModel = glmModel ? glmModel.id : this.availableModels[0].id
          }
        }
      } catch (error) {
        console.error('加载模型列表失败:', error)
      } finally {
        this.loadingModels = false
      }
    },
    filterOption(input, option) {
      return option.value.toLowerCase().includes(input.toLowerCase())
    },
    async sendMessage() {
      if (!this.inputMessage.trim() || this.loading) return

      const userMessage = {
        role: 'user',
        content: this.inputMessage.trim(),
        timestamp: new Date()
      }

      this.messages.push(userMessage)
      this.inputMessage = ''
      this.loading = true

      this.$nextTick(() => {
        this.scrollToBottom()
      })

      try {
        const requestMessages = this.messages
          .filter(msg => msg.role !== 'system')
          .map(msg => ({
            role: msg.role,
            content: msg.content
          }))

        const requestData = {
          messages: requestMessages,
          model: this.currentModel,
          system_prompt: this.settings.systemPrompt || undefined,
          temperature: this.settings.temperature,
          max_tokens: this.settings.maxTokens,
          stream: false
        }

        const response = await aiService.chat(requestData)

        if (response.data.success) {
          const assistantMessage = {
            role: 'assistant',
            content: response.data.content,
            timestamp: new Date(),
            model: response.data.model,
            usage: response.data.usage
          }

          this.messages.push(assistantMessage)
          this.saveChatHistory()

          this.$nextTick(() => {
            this.scrollToBottom()
          })
        } else {
          message.error(response.data.error || '对话失败')
          this.messages.pop()
        }
      } catch (error) {
        console.error('对话请求失败:', error)
        message.error(error.response?.data?.detail || '网络请求失败')
        this.messages.pop()
      } finally {
        this.loading = false
      }
    },

    clearChat() {
      this.messages = []
      this.saveChatHistory()
      message.success('对话已清空')
    },

    async copyMessage(content) {
      try {
        await navigator.clipboard.writeText(content)
        message.success('消息已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        message.error('复制失败')
      }
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    getTemperatureLabel() {
      if (this.settings.temperature <= 0.3) return '保守'
      if (this.settings.temperature <= 0.7) return '平衡'
      return '创意'
    },

    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },

    saveChatHistory() {
      try {
        localStorage.setItem('ai-chat-history', JSON.stringify(this.messages))
      } catch (error) {
        console.error('保存聊天记录失败:', error)
      }
    },

    loadChatHistory() {
      try {
        const history = localStorage.getItem('ai-chat-history')
        if (history) {
          this.messages = JSON.parse(history).map(msg => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }))
        }
      } catch (error) {
        console.error('加载聊天记录失败:', error)
      }
    },

    renderMarkdown(content) {
      if (!content) return ''
      marked.setOptions({
        highlight: function (code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(code, { language: lang }).value
            } catch (err) {
              console.error('代码高亮失败:', err)
            }
          }
          return hljs.highlightAuto(code).value
        },
        breaks: true,
        gfm: true
      })
      return marked.parse(content)
    },

    /**
     * 处理模型更新事件
     * 当模型配置被修改时，重新加载模型列表
     */
    async handleModelsUpdated(data) {
      console.log('收到模型更新通知:', data)
      message.info('模型列表已更新，正在刷新...', 2)

      // 重新加载模型列表（会从后端获取最新数据，因为缓存已被清除）
      await this.loadAvailableModels()

      // 如果当前选择的模型不在新的模型列表中，自动切换到第一个
      if (this.currentModel && !this.availableModels.some(m => m.id === this.currentModel)) {
        if (this.availableModels.length > 0) {
          const glmModel = this.availableModels.find(m =>
            m.id.includes('GLM-4') && !m.id.includes('V') && !m.id.includes('Vision')
          )
          this.currentModel = glmModel ? glmModel.id : this.availableModels[0].id
          message.warning('原模型已被移除，已自动切换到: ' + this.currentModel, 3)
        } else {
          this.currentModel = ''
          message.warning('当前没有可用模型，请先在模型管理页面配置', 4)
        }
      }
    }
  }
}
</script>

<style scoped>
.chat {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.chat-card {
  min-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.header-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
  max-height: calc(100vh - 400px);
}

.message {
  display: flex;
  margin-bottom: 20px;
  align-items: flex-start;
}

.user-message {
  flex-direction: row-reverse;
}

.user-message .message-content {
  background-color: #1677ff;
  color: #fff;
  margin-right: 12px;
}

.assistant-message .message-content {
  background-color: #f5f5f5;
  color: #333;
  margin-left: 12px;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 20px;
}

.user-message .message-avatar {
  background-color: #1677ff;
  color: #fff;
}

.assistant-message .message-avatar {
  background-color: #52c41a;
  color: #fff;
}

.message-content {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  position: relative;
}

/* Markdown 样式 */
.message-text :deep(h1),
.message-text :deep(h2),
.message-text :deep(h3),
.message-text :deep(h4),
.message-text :deep(h5),
.message-text :deep(h6) {
  margin: 12px 0 8px;
  font-weight: 600;
  line-height: 1.25;
}

.message-text :deep(h1) {
  font-size: 1.5em;
}

.message-text :deep(h2) {
  font-size: 1.3em;
}

.message-text :deep(h3) {
  font-size: 1.1em;
}

.message-text :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.message-text :deep(ul),
.message-text :deep(ol) {
  padding-left: 1.5em;
  margin: 8px 0;
}

.message-text :deep(li) {
  margin: 4px 0;
  line-height: 1.6;
}

.message-text :deep(code) {
  background-color: rgba(0, 0, 0, 0.06);
  border-radius: 3px;
  font-size: 85%;
  padding: 0.2em 0.4em;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.message-text :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  overflow: auto;
  margin: 8px 0;
  border: 1px solid #e9ecef;
}

.message-text :deep(pre code) {
  background-color: transparent;
  padding: 0;
  font-size: 90%;
  display: block;
  white-space: pre;
  line-height: 1.5;
}

.message-text :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  padding: 0 0.8em;
  color: #6a737d;
  margin: 8px 0;
}

.message-text :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
  font-size: 0.9em;
}

.message-text :deep(table th),
.message-text :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 10px;
}

.message-text :deep(table th) {
  background-color: rgba(0, 0, 0, 0.03);
  font-weight: 600;
}

.message-text :deep(hr) {
  border: none;
  border-top: 1px solid #e9ecef;
  margin: 12px 0;
}

.message-text :deep(a) {
  color: #0969da;
  text-decoration: none;
}

.message-text :deep(a:hover) {
  text-decoration: underline;
}

.message-text :deep(strong) {
  font-weight: 600;
}

.message-text :deep(em) {
  font-style: italic;
}

/* 用户消息中的 Markdown 样式调整 */
.user-message .message-text :deep(code) {
  background-color: rgba(255, 255, 255, 0.2);
}

.user-message .message-text :deep(pre) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.message-time {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 4px;
}

.message-actions {
  margin-left: 8px;
  display: flex;
}

.typing-indicator {
  display: flex;
  gap: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #999;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {

  0%,
  80%,
  100% {
    transform: scale(0);
  }

  40% {
    transform: scale(1);
  }
}

.input-container {
  border-top: 1px solid #e4e4e4;
  padding-top: 16px;
}

.advanced-settings {
  margin-bottom: 16px;
}

.collapse-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.slider-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider-label {
  font-size: 12px;
  color: #666;
}

.input-area {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-actions {
  display: flex;
  justify-content: flex-end;
}

:deep(.ant-card-body) {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px;
}
</style>
