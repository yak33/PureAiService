<template>
  <div class="code-assist">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>💻 代码助手</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="任务类型">
          <el-select v-model="form.task" placeholder="选择代码任务">
            <el-option label="代码审查" value="review" />
            <el-option label="代码优化" value="optimize" />
            <el-option label="代码解释" value="explain" />
            <el-option label="错误调试" value="debug" />
            <el-option label="代码生成" value="generate" />
            <el-option label="语言转换" value="convert" />
            <el-option label="编写测试" value="test" />
            <el-option label="生成文档" value="document" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="编程语言">
          <el-select v-model="form.language" placeholder="选择编程语言">
            <el-option label="Python" value="Python" />
            <el-option label="JavaScript" value="JavaScript" />
            <el-option label="Java" value="Java" />
            <el-option label="C++" value="C++" />
            <el-option label="Go" value="Go" />
            <el-option label="Rust" value="Rust" />
            <el-option label="TypeScript" value="TypeScript" />
            <el-option label="PHP" value="PHP" />
            <el-option label="C#" value="C#" />
            <el-option label="其他" value="Other" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="具体要求">
          <el-input
            v-model="form.requirements"
            type="textarea"
            :rows="3"
            placeholder="描述您的具体需求或问题..."
          />
        </el-form-item>
        
        <el-form-item label="代码内容" v-if="form.task !== 'generate'">
          <el-input
            v-model="form.code"
            type="textarea"
            :rows="12"
            placeholder="粘贴您的代码..."
            show-word-limit
            maxlength="8000"
            class="code-input"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="processCode"
            :loading="loading"
            :disabled="!canProcess"
          >
            <el-icon><Tools /></el-icon>
            {{ getButtonText() }}
          </el-button>
          <el-button @click="clearForm">
            <el-icon><Delete /></el-icon>
            清空内容
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <span>🚀 处理结果</span>
          <div>
            <el-button
              type="text"
              @click="copyResult"
              :icon="DocumentCopy"
            >
              复制结果
            </el-button>
            <el-button
              type="text"
              @click="downloadCode"
              :icon="Download"
              v-if="hasCodeInResult"
            >
              下载代码
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="result-content">
        <div class="result-meta">
          <el-tag type="info">任务: {{ result.task }}</el-tag>
          <el-tag type="success" v-if="result.language">语言: {{ result.language }}</el-tag>
          <el-tag type="warning" v-if="result.usage">
            Token: {{ result.usage.total_tokens || '未知' }}
          </el-tag>
        </div>
        
        <div class="result-text">
          <pre><code>{{ result.result }}</code></pre>
        </div>
      </div>
    </el-card>
    
    <el-card v-if="error" class="error-card">
      <template #header>
        <div class="card-header">
          <span>❌ 错误信息</span>
        </div>
      </template>
      <p>{{ error }}</p>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { DocumentCopy, Download } from '@element-plus/icons-vue'

export default {
  name: 'CodeAssist',
  components: {
    DocumentCopy,
    Download
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
        'review': '开始审查',
        'optimize': '开始优化',
        'explain': '开始解释',
        'debug': '开始调试',
        'generate': '生成代码',
        'convert': '转换代码',
        'test': '生成测试',
        'document': '生成文档'
      }
      return taskTexts[this.form.task] || '开始处理'
    },
    
    async processCode() {
      if (!this.canProcess) {
        ElMessage.warning('请填写必要的信息')
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
        
        const response = await axios.post('/api/v1/ai/code', requestData)
        
        if (response.data.success) {
          this.result = response.data
          ElMessage.success('代码处理完成')
        } else {
          this.error = response.data.error || '处理失败'
          ElMessage.error('处理失败')
        }
      } catch (error) {
        console.error('处理请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        ElMessage.error('处理请求失败')
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
          ElMessage.success('结果已复制到剪贴板')
        } catch (error) {
          console.error('复制失败:', error)
          ElMessage.error('复制失败')
        }
      }
    },
    
    downloadCode() {
      if (!this.result?.result) return
      
      const extensions = {
        'Python': '.py',
        'JavaScript': '.js',
        'Java': '.java',
        'C++': '.cpp',
        'Go': '.go',
        'Rust': '.rs',
        'TypeScript': '.ts',
        'PHP': '.php',
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
      
      ElMessage.success('代码文件已下载')
    }
  }
}
</script>

<style scoped>
.code-assist {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-card {
  margin-top: 20px;
}

.error-card {
  margin-top: 20px;
}

.code-input {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.code-input :deep(.el-textarea__inner) {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.result-content {
  padding: 10px 0;
}

.result-meta {
  margin-bottom: 16px;
}

.result-meta .el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
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

.result-text code {
  font-family: inherit;
}

.error-card p {
  color: #f56c6c;
  margin: 0;
}
</style>