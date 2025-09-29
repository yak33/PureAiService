<template>
  <div class="text-analysis">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="📝 文本分析">
          <a-form :model="form" layout="vertical">
            <a-form-item label="分析任务">
              <a-select v-model:value="form.task" placeholder="选择分析任务">
                <a-select-option value="analyze">综合分析</a-select-option>
                <a-select-option value="summarize">内容摘要</a-select-option>
                <a-select-option value="extract">信息提取</a-select-option>
                <a-select-option value="translate">语言翻译</a-select-option>
                <a-select-option value="sentiment">情感分析</a-select-option>
                <a-select-option value="classify">文本分类</a-select-option>
                <a-select-option value="keywords">关键词提取</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="AI模型">
              <a-select v-model:value="form.model" placeholder="选择AI模型（默认GLM-4.5）">
                <a-select-option value="zai-org/GLM-4.5">GLM-4.5 (推荐)</a-select-option>
                <a-select-option value="moonshotai/Kimi-K2-Instruct-0905">Kimi-K2</a-select-option>
              </a-select>
            </a-form-item>

            <a-form-item label="自定义提示">
              <a-textarea
                v-model:value="form.customPrompt"
                :rows="2"
                placeholder="可选：输入自定义分析要求"
                :auto-size="{ minRows: 2, maxRows: 6 }"
              />
            </a-form-item>

            <a-form-item label="文本内容">
              <a-textarea
                v-model:value="form.text"
                :rows="8"
                placeholder="请输入要分析的文本内容..."
                :maxlength="5000"
                show-count
                :auto-size="{ minRows: 8, maxRows: 16 }"
              />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button
                  type="primary"
                  @click="analyzeText"
                  :loading="loading"
                  :disabled="!form.text.trim()"
                >
                  <HighlightOutlined />
                  <span>开始分析</span>
                </a-button>
                <a-button @click="clearForm">
                  <DeleteOutlined />
                  <span>清空内容</span>
                </a-button>
              </a-space>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <a-col :span="24" :lg="12">
        <a-card class="result-card" title="📊 分析结果" :loading="loading">
          <template #extra>
            <a-button type="link" @click="copyResult" :disabled="!result">
              <CopyOutlined />
              <span>复制结果</span>
            </a-button>
          </template>

          <div v-if="result" class="result-content">
            <div class="result-meta">
              <a-tag color="processing">任务: {{ result.task }}</a-tag>
              <a-tag color="success" v-if="result.model">模型: {{ result.model }}</a-tag>
              <a-tag color="warning" v-if="result.usage">
                Token: {{ result.usage.total_tokens || '未知' }}
              </a-tag>
            </div>

            <div class="result-text">
              <pre>{{ result.result }}</pre>
            </div>
          </div>

          <div v-else class="result-placeholder">
            <a-empty description="请先提交文本以查看分析结果" />
          </div>
        </a-card>

        <a-alert
          v-if="error"
          type="error"
          show-icon
          class="error-alert"
          :message="error"
        />
      </a-col>
    </a-row>
  </div>
</template>

<script>
import axios from 'axios'
import { message } from 'ant-design-vue'
import { CopyOutlined, HighlightOutlined, DeleteOutlined } from '@ant-design/icons-vue'

export default {
  name: 'TextAnalysis',
  components: {
    CopyOutlined,
    HighlightOutlined,
    DeleteOutlined
  },
  data() {
    return {
      loading: false,
      form: {
        text: '',
        task: 'analyze',
        model: 'zai-org/GLM-4.5',
        customPrompt: ''
      },
      result: null,
      error: null
    }
  },
  methods: {
    async analyzeText() {
      if (!this.form.text.trim()) {
        message.warning('请输入要分析的文本内容')
        return
      }

      this.loading = true
      this.result = null
      this.error = null

      try {
        const requestData = {
          text: this.form.text,
          task: this.form.task,
          model: this.form.model || undefined,
          custom_prompt: this.form.customPrompt || undefined
        }

        const response = await axios.post('/api/v1/ai/text/analyze', requestData)

        if (response.data.success) {
          this.result = response.data
          message.success('文本分析完成')
        } else {
          this.error = response.data.error || '分析失败'
          message.error('分析失败')
        }
      } catch (error) {
        console.error('分析请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        message.error('分析请求失败')
      } finally {
        this.loading = false
      }
    },

    clearForm() {
      this.form.text = ''
      this.form.customPrompt = ''
      this.result = null
      this.error = null
    },

    async copyResult() {
      if (this.result?.result) {
        try {
          await navigator.clipboard.writeText(this.result.result)
          message.success('结果已复制到剪贴板')
        } catch (error) {
          console.error('复制失败:', error)
          message.error('复制失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.text-analysis {
  padding: 20px;
}

.form-card {
  border-radius: 8px;
  height: 100%;
}

.result-card {
  height: 100%;
}

.result-content {
  padding: 10px 0;
}

.result-meta {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.result-meta :deep(.ant-tag) {
  margin-right: 0;
}

.result-text {
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.result-text pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.result-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.error-alert {
  margin-top: 16px;
}
</style>