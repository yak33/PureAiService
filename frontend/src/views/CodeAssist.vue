<template>
  <div class="code-assist">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="💻 代码助手">
          <a-form :model="form" layout="vertical">
        <a-row :gutter="20">
          <a-col :span="24" :md="12">
            <a-form-item label="任务类型">
              <a-select v-model:value="form.task" placeholder="选择代码任务">
                <a-select-option value="review">代码审查</a-select-option>
                <a-select-option value="optimize">代码优化</a-select-option>
                <a-select-option value="explain">代码解释</a-select-option>
                <a-select-option value="debug">错误调试</a-select-option>
                <a-select-option value="generate">代码生成</a-select-option>
                <a-select-option value="convert">语言转换</a-select-option>
                <a-select-option value="test">编写测试</a-select-option>
                <a-select-option value="document">生成文档</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :span="24" :md="12">
            <a-form-item label="编程语言">
              <a-select v-model:value="form.language" placeholder="选择编程语言">
                <a-select-option value="Python">Python</a-select-option>
                <a-select-option value="JavaScript">JavaScript</a-select-option>
                <a-select-option value="TypeScript">TypeScript</a-select-option>
                <a-select-option value="Java">Java</a-select-option>
                <a-select-option value="C++">C++</a-select-option>
                <a-select-option value="Go">Go</a-select-option>
                <a-select-option value="Rust">Rust</a-select-option>
                <a-select-option value="PHP">PHP</a-select-option>
                <a-select-option value="C#">C#</a-select-option>
                <a-select-option value="Other">其他</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="具体要求">
          <a-textarea
            v-model:value="form.requirements"
            :rows="3"
            placeholder="描述您的具体需求或问题..."
            :auto-size="{ minRows: 3, maxRows: 8 }"
          />
        </a-form-item>

        <a-form-item v-if="form.task !== 'generate'" label="代码内容">
          <a-textarea
            v-model:value="form.code"
            :rows="12"
            placeholder="粘贴您的代码..."
            :maxlength="8000"
            show-count
            :auto-size="{ minRows: 12, maxRows: 20 }"
            class="code-textarea"
          />
        </a-form-item>

            <a-form-item>
              <a-space>
                <a-button
                  type="primary"
                  @click="processCode"
                  :loading="loading"
                  :disabled="!canProcess"
                >
                  <ToolOutlined />
                  <span>{{ getButtonText() }}</span>
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
        <a-card class="result-card" title="🚀 处理结果" :loading="loading" :bordered="true">
          <template #extra>
            <a-space>
              <a-button type="link" @click="copyResult" :disabled="!result">
                <CopyOutlined />
                <span>复制结果</span>
              </a-button>
              <a-button type="link" v-if="hasCodeInResult" @click="downloadCode">
                <DownloadOutlined />
                <span>下载代码</span>
              </a-button>
            </a-space>
          </template>

          <div v-if="result" class="result-content">
            <div class="result-meta">
              <a-tag color="processing">任务: {{ result.task }}</a-tag>
              <a-tag color="success" v-if="result.language">语言: {{ result.language }}</a-tag>
              <a-tag color="warning" v-if="result.usage">
                Token: {{ result.usage.total_tokens || '未知' }}
              </a-tag>
            </div>

            <div class="result-text">
              <pre><code>{{ result.result }}</code></pre>
            </div>
          </div>

          <div v-else class="result-placeholder">
            <a-empty description="请先提交任务以查看结果" />
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
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import {
  ToolOutlined,
  DeleteOutlined,
  CopyOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'CodeAssist',
  components: {
    ToolOutlined,
    DeleteOutlined,
    CopyOutlined,
    DownloadOutlined
  },
  data() {
    return {
      loading: false,
      form: {
        code: '',
        task: 'review',
        language: 'Python',
        requirements: ''
      },
      result: null,
      error: null
    }
  },
  computed: {
    canProcess() {
      if (this.form.task === 'generate') {
        return this.form.requirements && this.form.requirements.trim()
      }
      return this.form.code && this.form.code.trim()
    },
    hasCodeInResult() {
      return this.result && (
        this.result.result.includes('```') ||
        this.form.task === 'generate' ||
        this.form.task === 'optimize'
      )
    }
  },
  methods: {
    getButtonText() {
      const taskTexts = {
        review: '开始审查',
        optimize: '开始优化',
        explain: '开始解释',
        debug: '开始调试',
        generate: '生成代码',
        convert: '转换代码',
        test: '生成测试',
        document: '生成文档'
      }
      return taskTexts[this.form.task] || '开始处理'
    },

    async processCode() {
      if (!this.canProcess) {
        message.warning('请填写必要的信息')
        return
      }

      this.loading = true
      this.result = null
      this.error = null

      try {
        const requestData = {
          task: this.form.task,
          language: this.form.language,
          requirements: this.form.requirements || undefined,
          code: this.form.task !== 'generate' ? this.form.code : undefined
        }

        const response = await aiService.codeAssist(requestData)

        if (response.data.success) {
          this.result = response.data
          message.success('代码处理完成')
        } else {
          this.error = response.data.error || '处理失败'
          message.error('处理失败')
        }
      } catch (error) {
        console.error('处理请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        message.error('处理请求失败')
      } finally {
        this.loading = false
      }
    },

    clearForm() {
      this.form.code = ''
      this.form.requirements = ''
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
    },

    downloadCode() {
      if (!this.result?.result) return

      const extensions = {
        Python: '.py',
        JavaScript: '.js',
        Java: '.java',
        'C++': '.cpp',
        Go: '.go',
        Rust: '.rs',
        TypeScript: '.ts',
        PHP: '.php',
        'C#': '.cs'
      }

      const extension = extensions[this.form.language] || '.txt'
      const filename = `code_${this.form.task}_${Date.now()}${extension}`

      const blob = new Blob([this.result.result], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(url)

      message.success('代码文件已下载')
    }
  }
}
</script>

<style scoped>

.code-assist {
  padding: 20px;
}

.form-card {
  border-radius: 8px;
  height: 100%;
}

.code-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.code-textarea :deep(.ant-input) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
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
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
}

.result-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.result-card {
  border-radius: 8px;
  height: 100%;
}

.error-alert {
  margin-top: 16px;
}
</style>