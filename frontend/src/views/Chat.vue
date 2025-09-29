<template>
  <div class="chat">
    <a-card class="chat-card">
      <template #title>
        <div class="card-header">
          <span>💬 智能对话</span>
          <div class="header-controls">
            <a-select
              v-model:value="currentModel"
              size="small"
              style="width: 200px"
            >
              <a-select-option value="zai-org/GLM-4.5">GLM-4.5 (推荐)</a-select-option>
              <a-select-option value="moonshotai/Kimi-K2-Instruct-0905">Kimi-K2</a-select-option>
            </a-select>
            <a-button size="small" @click="clearChat">
              <DeleteOutlined />
              <span>清空对话</span>
            </a-button>
          </div>
        </div>
      </template>

      <div class="chat-container">
        <div class="messages-container" ref="messagesContainer">
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="['message', message.role === 'user' ? 'user-message' : 'assistant-message']"
          >
            <div class="message-avatar">
              <UserOutlined v-if="message.role === 'user'" />
              <RobotOutlined v-else />
            </div>
            <div class="message-content">
              <div class="message-text">
                <pre>{{ message.content }}</pre>
              </div>
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
                  <a-textarea
                    v-model:value="settings.systemPrompt"
                    :rows="2"
                    placeholder="可选：设置AI的角色和行为..."
                    :auto-size="{ minRows: 2, maxRows: 6 }"
                  />
                </a-form-item>
                <a-form-item label="温度参数">
                  <div class="slider-wrapper">
                    <a-slider
                      v-model:value="settings.temperature"
                      :min="0"
                      :max="1"
                      :step="0.1"
                    />
                    <span class="slider-label">{{ settings.temperature }} ({{ getTemperatureLabel() }})</span>
                  </div>
                </a-form-item>
                <a-form-item label="最大Token">
                  <a-input-number
                    v-model:value="settings.maxTokens"
                    :min="100"
                    :max="4000"
                    :step="100"
                  />
                </a-form-item>
              </a-form>
            </a-collapse-panel>
          </a-collapse>

          <div class="input-area">
            <a-textarea
              v-model:value="inputMessage"
              :rows="3"
              placeholder="输入您的问题..."
              :auto-size="{ minRows: 3, maxRows: 6 }"
              @keydown.ctrl.enter="sendMessage"
              :disabled="loading"
            />
            <div class="input-actions">
              <a-button
                type="primary"
                @click="sendMessage"
                :loading="loading"
                :disabled="!inputMessage.trim()"
              >
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
      currentModel: 'zai-org/GLM-4.5',
      showAdvanced: [],
      settings: {
        systemPrompt: '',
        temperature: 0.7,
        maxTokens: 2000
      }
    }
  },
  mounted() {
    this.loadChatHistory()
  },
  methods: {
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

.message-text pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
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
  0%, 80%, 100% {
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