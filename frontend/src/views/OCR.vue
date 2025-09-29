<template>
  <div class="ocr">
    <a-card class="form-card" title="📷 文字识别 (OCR)">
      <a-form :model="form" layout="vertical">
        <a-row :gutter="20">
          <a-col :span="24" :md="12">
            <a-form-item label="识别语言">
              <a-select v-model:value="form.language" placeholder="选择识别语言">
                <a-select-option value="auto">自动识别</a-select-option>
                <a-select-option value="zh">中文</a-select-option>
                <a-select-option value="en">英文</a-select-option>
                <a-select-option value="mix">中英文混合</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <a-col :span="24" :md="12">
            <a-form-item label="识别精度">
              <a-select v-model:value="form.detailLevel" placeholder="选择识别精度">
                <a-select-option value="high">高精度（慢）</a-select-option>
                <a-select-option value="medium">标准精度</a-select-option>
                <a-select-option value="low">快速识别</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="上传图片">
          <a-upload-dragger
            name="file"
            :show-upload-list="false"
            :before-upload="handleBeforeUpload"
            accept="image/*"
          >
            <div v-if="!imageFile" class="upload-area">
              <UploadOutlined class="upload-icon" />
              <p class="upload-text">将图片拖拽到此处，或<em>点击上传</em></p>
              <p class="upload-tip">支持 JPG、PNG、GIF、WebP 格式，文件大小不超过 10MB</p>
            </div>
            <div v-else class="image-preview">
              <img :src="imagePreview" alt="预览图片" />
              <div class="image-info">
                <p>{{ imageFile.name }}</p>
                <p>{{ formatFileSize(imageFile.size) }}</p>
              </div>
            </div>
          </a-upload-dragger>
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button
              type="primary"
              @click="recognizeText"
              :loading="loading"
              :disabled="!imageFile"
            >
              <HighlightOutlined />
              <span>开始识别</span>
            </a-button>
            <a-button v-if="imageFile" @click="clearImage">
              <DeleteOutlined />
              <span>重新选择</span>
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>

    <a-card v-if="result" class="result-card" title="📝 识别结果">
      <template #extra>
        <a-space>
          <a-button type="link" @click="copyResult">
            <CopyOutlined />
            <span>复制文本</span>
          </a-button>
          <a-button type="link" @click="downloadText">
            <DownloadOutlined />
            <span>下载文本</span>
          </a-button>
        </a-space>
      </template>

      <div class="result-content">
        <div class="result-meta">
          <a-tag color="processing">语言: {{ form.language }}</a-tag>
          <a-tag color="success">精度: {{ form.detailLevel }}</a-tag>
          <a-tag color="warning" v-if="result.usage">
            Token: {{ result.usage.total_tokens || '未知' }}
          </a-tag>
        </div>

        <div class="result-text">
          <pre>{{ result.text }}</pre>
        </div>

        <div class="result-stats">
          <p>识别文字数量: {{ result.text.length }} 字符</p>
          <p>处理时间: {{ processingTime }}ms</p>
        </div>
      </div>
    </a-card>

    <a-alert
      v-if="error"
      type="error"
      show-icon
      class="error-alert"
      :message="error"
    />

    <a-alert
      type="info"
      show-icon
      class="helper-alert"
      message="提示"
    >
      <template #description>
        支持多语言识别，建议使用高质量图片以获得更好效果。
      </template>
    </a-alert>
  </div>
</template>

<script>
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import {
  UploadOutlined,
  HighlightOutlined,
  DeleteOutlined,
  CopyOutlined,
  DownloadOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'OCR',
  components: {
    UploadOutlined,
    HighlightOutlined,
    DeleteOutlined,
    CopyOutlined,
    DownloadOutlined
  },
  data() {
    return {
      loading: false,
      form: {
        language: 'auto',
        detailLevel: 'medium'
      },
      imageFile: null,
      imagePreview: null,
      result: null,
      error: null,
      processingTime: 0
    }
  },
  methods: {
    handleBeforeUpload(file) {
      if (file.size > 10 * 1024 * 1024) {
        message.error('文件大小不能超过 10MB')
        return false
      }

      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 JPG、PNG、GIF、WebP 格式的图片')
        return false
      }

      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }

      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
      this.result = null
      this.error = null
      return false
    },

    async recognizeText() {
      if (!this.imageFile) {
        message.warning('请先上传图片')
        return
      }

      this.loading = true
      this.result = null
      this.error = null
      const startTime = Date.now()

      try {
        const formData = new FormData()
        formData.append('file', this.imageFile)
        formData.append('language', this.form.language)
        formData.append('detail_level', this.form.detailLevel)

        const response = await aiService.ocr(formData)

        this.processingTime = Date.now() - startTime

        if (response.data.success) {
          this.result = response.data
          message.success('文字识别完成')
        } else {
          this.error = response.data.error || '识别失败'
          message.error('识别失败')
        }
      } catch (error) {
        console.error('识别请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        message.error('识别请求失败')
      } finally {
        this.loading = false
      }
    },

    clearImage() {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }
      this.imageFile = null
      this.imagePreview = null
      this.result = null
      this.error = null
    },

    async copyResult() {
      if (this.result?.text) {
        try {
          await navigator.clipboard.writeText(this.result.text)
          message.success('文本已复制到剪贴板')
        } catch (error) {
          console.error('复制失败:', error)
          message.error('复制失败')
        }
      }
    },

    downloadText() {
      if (!this.result?.text) return

      const filename = `ocr_result_${Date.now()}.txt`
      const blob = new Blob([this.result.text], { type: 'text/plain;charset=utf-8' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.click()
      window.URL.revokeObjectURL(url)

      message.success('文本文件已下载')
    },

    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
    }
  },

  beforeUnmount() {
    if (this.imagePreview) {
      URL.revokeObjectURL(this.imagePreview)
    }
  }
}
</script>

<style scoped>
.ocr {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.form-card {
  border-radius: 8px;
}

.upload-area {
  text-align: center;
  padding: 40px 20px;
}

.upload-icon {
  font-size: 64px;
  color: #999;
}

.upload-text {
  color: #606266;
  font-size: 14px;
}

.upload-text em {
  color: #1677ff;
  font-style: normal;
  margin-left: 4px;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
}

.image-preview {
  text-align: center;
  padding: 20px;
}

.image-preview img {
  max-width: 100%;
  max-height: 300px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-info {
  margin-top: 12px;
  color: #666;
  font-size: 12px;
}

.result-card {
  margin-top: 20px;
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
  margin-bottom: 16px;
}

.result-text pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.result-stats {
  padding-top: 12px;
  border-top: 1px solid #e4e4e4;
  color: #666;
  font-size: 12px;
}

.error-alert {
  margin-top: 20px;
}

.helper-alert {
  margin-top: 20px;
}

.image-preview {
  text-align: center;
  padding: 20px;
}

.image-preview img {
  max-height: 300px;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.image-info {
  margin-top: 12px;
}

.image-info p {
  margin: 4px 0;
  color: #666;
  font-size: 12px;
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
  margin-bottom: 16px;
}

.result-text pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;
  color: #333;
}

.result-stats {
  padding-top: 12px;
  border-top: 1px solid #e4e4e4;
}

.result-stats p {
  margin: 4px 0;
  color: #666;
  font-size: 12px;
}

.error-card p {
  color: #f56c6c;
  margin: 0;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}
</style>