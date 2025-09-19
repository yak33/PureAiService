<template>
  <div class="ocr">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>📷 文字识别 (OCR)</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="识别语言">
          <el-select v-model="form.language" placeholder="选择识别语言">
            <el-option label="自动识别" value="auto" />
            <el-option label="中文" value="zh" />
            <el-option label="英文" value="en" />
            <el-option label="中英文混合" value="mix" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="识别精度">
          <el-select v-model="form.detailLevel" placeholder="选择识别精度">
            <el-option label="高精度（慢）" value="high" />
            <el-option label="标准精度" value="medium" />
            <el-option label="快速识别" value="low" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="上传图片">
          <el-upload
            class="upload-demo"
            drag
            :auto-upload="false"
            :on-change="handleFileChange"
            :show-file-list="false"
            accept="image/*"
          >
            <div v-if="!imageFile" class="upload-area">
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                将图片拖拽到此处，或<em>点击上传</em>
              </div>
              <div class="el-upload__tip">
                支持 JPG、PNG、GIF 格式，文件大小不超过 10MB
              </div>
            </div>
            <div v-else class="image-preview">
              <img :src="imagePreview" alt="预览图片" />
              <div class="image-info">
                <p>{{ imageFile.name }}</p>
                <p>{{ formatFileSize(imageFile.size) }}</p>
              </div>
            </div>
          </el-upload>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="recognizeText"
            :loading="loading"
            :disabled="!imageFile"
          >
            <el-icon><MagicStick /></el-icon>
            开始识别
          </el-button>
          <el-button @click="clearImage" v-if="imageFile">
            <el-icon><Delete /></el-icon>
            重新选择
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="result" class="result-card">
      <template #header>
        <div class="card-header">
          <span>📝 识别结果</span>
          <div>
            <el-button
              type="text"
              @click="copyResult"
              :icon="DocumentCopy"
            >
              复制文本
            </el-button>
            <el-button
              type="text"
              @click="downloadText"
              :icon="Download"
            >
              下载文本
            </el-button>
          </div>
        </div>
      </template>
      
      <div class="result-content">
        <div class="result-meta">
          <el-tag type="info">语言: {{ form.language }}</el-tag>
          <el-tag type="success">精度: {{ form.detailLevel }}</el-tag>
          <el-tag type="warning" v-if="result.usage">
            Token: {{ result.usage.total_tokens || '未知' }}
          </el-tag>
        </div>
        
        <div class="result-text">
          <pre>{{ result.text }}</pre>
        </div>
        
        <div class="result-stats">
          <p>识别文字数量: {{ result.text.length }} 字符</p>
          <p>处理时间: {{ processingTime }}ms</p>
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
import { DocumentCopy, Download, UploadFilled } from '@element-plus/icons-vue'

export default {
  name: 'OCR',
  components: {
    DocumentCopy,
    Download,
    UploadFilled
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
    handleFileChange(file) {
      if (file.size > 10 * 1024 * 1024) {
        ElMessage.error('文件大小不能超过 10MB')
        return
      }
      
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.raw.type)) {
        ElMessage.error('只支持 JPG、PNG、GIF、WebP 格式的图片')
        return
      }
      
      this.imageFile = file.raw
      this.imagePreview = URL.createObjectURL(file.raw)
      this.result = null
      this.error = null
    },
    
    async recognizeText() {
      if (!this.imageFile) {
        ElMessage.warning('请先上传图片')
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
        
        const response = await axios.post('/api/v1/ai/ocr', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        this.processingTime = Date.now() - startTime
        
        if (response.data.success) {
          this.result = response.data
          ElMessage.success('文字识别完成')
        } else {
          this.error = response.data.error || '识别失败'
          ElMessage.error('识别失败')
        }
      } catch (error) {
        console.error('识别请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        ElMessage.error('识别请求失败')
      } finally {
        this.loading = false
      }
    },
    
    clearImage() {
      this.imageFile = null
      this.imagePreview = null
      this.result = null
      this.error = null
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }
    },
    
    async copyResult() {
      if (this.result?.text) {
        try {
          await navigator.clipboard.writeText(this.result.text)
          ElMessage.success('文本已复制到剪贴板')
        } catch (error) {
          console.error('复制失败:', error)
          ElMessage.error('复制失败')
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
      
      ElMessage.success('文本文件已下载')
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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

.upload-area {
  text-align: center;
  padding: 40px 20px;
}

.upload-area .el-icon--upload {
  font-size: 67px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-area .el-upload__text {
  color: #606266;
  font-size: 14px;
  margin-bottom: 8px;
}

.upload-area .el-upload__tip {
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