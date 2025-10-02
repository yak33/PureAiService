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
              <a-select 
                v-model:value="form.model" 
                placeholder="选择AI模型" 
                :loading="loadingModels"
                show-search
                :filter-option="filterOption"
              >
                <a-select-option 
                  v-for="model in availableModels" 
                  :key="model.id" 
                  :value="model.id"
                >
                  {{ model.id }}
                </a-select-option>
              </a-select>
              <div v-if="!loadingModels && availableModels.length === 0" style="margin-top: 8px;">
                <a-alert type="warning" message="请先在模型管理页面配置可用模型" show-icon />
              </div>
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

          <div v-else-if="error" class="result-placeholder">
            <a-result
              status="error"
              title="分析失败"
              :sub-title="error"
            >
              <template #extra>
                <a-button type="primary" @click="error = null">
                  知道了
                </a-button>
              </template>
            </a-result>
          </div>

          <div v-else class="result-placeholder">
            <a-empty description="请先提交文本以查看分析结果" />
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import { CopyOutlined, HighlightOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { getCachedModels, setCachedModels } from '../utils/modelCache'

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
      loadingModels: false,
      availableModels: [],
      form: {
        text: '',
        task: 'analyze',
        model: '',
        customPrompt: ''
      },
      result: null,
      error: null
    }
  },
  async mounted() {
    await this.loadAvailableModels()
  },
  methods: {
    async loadAvailableModels() {
      // 先尝试从缓存读取
      const cachedModels = getCachedModels()
      if (cachedModels && cachedModels.length > 0) {
        this.availableModels = cachedModels
        if (!this.form.model) {
          const glmModel = this.availableModels.find(m => 
            m.id.includes('GLM-4') && !m.id.includes('V') && !m.id.includes('Vision')
          )
          this.form.model = glmModel ? glmModel.id : this.availableModels[0].id
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
          if (!this.form.model && this.availableModels.length > 0) {
            const glmModel = this.availableModels.find(m => 
              m.id.includes('GLM-4') && !m.id.includes('V') && !m.id.includes('Vision')
            )
            this.form.model = glmModel ? glmModel.id : this.availableModels[0].id
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

        const response = await aiService.analyzeText(requestData)

        if (response.data.success) {
          this.result = response.data
          message.success('文本分析完成')
        } else {
          const errorMsg = response.data.error || '分析失败'
          this.error = `${errorMsg}。可能模型不适配，请切换其他模型。`
        }
      } catch (error) {
        console.error('分析请求失败:', error)
        const errorMsg = error.response?.data?.detail || '网络请求失败'
        this.error = `${errorMsg}。可能模型不适配，请切换其他模型。`
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
  max-height: 600px;
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
</style>
