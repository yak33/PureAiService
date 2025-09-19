<template>
  <div class="text-analysis">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📝 文本分析</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="分析任务">
          <el-select v-model="form.task" placeholder="选择分析任务">
            <el-option label="综合分析" value="analyze" />
            <el-option label="内容摘要" value="summarize" />
            <el-option label="信息提取" value="extract" />
            <el-option label="语言翻译" value="translate" />
            <el-option label="情感分析" value="sentiment" />
            <el-option label="文本分类" value="classify" />
            <el-option label="关键词提取" value="keywords" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="AI模型">
          <el-select v-model="form.model" placeholder="选择AI模型（默认GLM-4.5）">
            <el-option label="GLM-4.5 (推荐)" value="zai-org/GLM-4.5" />
            <el-option label="Kimi-K2" value="moonshotai/Kimi-K2-Instruct-0905" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="自定义提示">
          <el-input
            v-model="form.customPrompt"
            type="textarea"
            :rows="2"
            placeholder="可选：输入自定义分析要求"
          />
        </el-form-item>
        
        <el-form-item label="文本内容">
          <el-input
            v-model="form.text"
            type="textarea"
            :rows="8"
            placeholder="请输入要分析的文本内容..."
            show-word-limit
            maxlength="5000"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="analyzeText"
            :loading="loading"
            :disabled="!form.text.trim()"
          >
            <el-icon><MagicStick /></el-icon>
            开始分析
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
          <span>📊 分析结果</span>
          <el-button
            type="text"
            @click="copyResult"
            :icon="DocumentCopy"
          >
            复制结果
          </el-button>
        </div>
      </template>
      
      <div class="result-content">
        <div class="result-meta">
          <el-tag type="info">任务: {{ result.task }}</el-tag>
          <el-tag type="success" v-if="result.model">模型: {{ result.model }}</el-tag>
          <el-tag type="warning" v-if="result.usage">
            Token: {{ result.usage.total_tokens || '未知' }}
          </el-tag>
        </div>
        
        <div class="result-text">
          <pre>{{ result.result }}</pre>
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
import { DocumentCopy } from '@element-plus/icons-vue'

export default {
  name: 'TextAnalysis',
  components: {
    DocumentCopy
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
        ElMessage.warning('请输入要分析的文本内容')
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
          ElMessage.success('文本分析完成')
        } else {
          this.error = response.data.error || '分析失败'
          ElMessage.error('分析失败')
        }
      } catch (error) {
        console.error('分析请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        ElMessage.error('分析请求失败')
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
          ElMessage.success('结果已复制到剪贴板')
        } catch (error) {
          console.error('复制失败:', error)
          ElMessage.error('复制失败')
        }
      }
    }
  }
}
</script>

<style scoped>
.text-analysis {
  padding: 20px;
  max-width: 1000px;
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

.error-card p {
  color: #f56c6c;
  margin: 0;
}
</style>