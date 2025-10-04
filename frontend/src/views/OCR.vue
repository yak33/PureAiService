<template>
  <div class="ocr">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="📷 文字识别 (OCR)">
          <a-form :model="form" layout="vertical">
            <a-row :gutter="20">
              <a-col :span="24" :md="8">
                <a-form-item label="识别语言">
                  <a-select v-model:value="form.language" placeholder="选择识别语言">
                    <a-select-option value="auto">自动识别</a-select-option>
                    <a-select-option value="zh">中文</a-select-option>
                    <a-select-option value="en">英文</a-select-option>
                    <a-select-option value="mix">中英文混合</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>

              <a-col :span="24" :md="8">
                <a-form-item label="识别精度">
                  <a-select v-model:value="form.detailLevel" placeholder="选择识别精度">
                    <a-select-option value="high">高精度（慢）</a-select-option>
                    <a-select-option value="medium">标准精度</a-select-option>
                    <a-select-option value="low">快速识别</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>

              <a-col :span="24" :md="8">
                <a-form-item label="视觉模型">
                  <a-select 
                    v-model:value="form.model" 
                    placeholder="选择视觉模型" 
                    :loading="loadingModels"
                    show-search
                    :filter-option="filterOption"
                  >
                    <a-select-option 
                      v-for="model in visionModels" 
                      :key="model.id" 
                      :value="model.id"
                    >
                      {{ model.id }}
                    </a-select-option>
                  </a-select>
                  <div v-if="!loadingModels && visionModels.length === 0" style="margin-top: 8px;">
                    <a-alert type="warning" message="请先在模型管理页面配置视觉模型" show-icon />
                  </div>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="上传图片">
              <a-upload-dragger 
                name="file" 
                :show-upload-list="false" 
                :before-upload="handleBeforeUpload" 
                accept="image/*"
                @paste.native="handlePaste"
              >
                <div v-if="!imageFile" class="upload-area">
                  <UploadOutlined class="upload-icon" />
                  <p class="upload-text">将图片拖拽到此处，或<em>点击上传</em></p>
                  <p class="upload-tip">支持 JPG、PNG、GIF、WebP 格式，文件大小不超过 10MB，图片尺寸需大于 28×28 像素</p>
                  <p class="paste-tip">📋 也可以直接 <strong>Ctrl+V</strong> 粘贴图片</p>
                </div>
                <div v-else class="image-preview">
                  <img :src="imagePreview" alt="预览图片" @click.stop="showImageModal" class="clickable-image" />
                  <div class="image-info">
                    <p>{{ imageFile.name }}</p>
                    <p>{{ formatFileSize(imageFile.size) }}</p>
                  </div>
                </div>
              </a-upload-dragger>
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button type="primary" @click="recognizeText" :loading="loading" :disabled="!imageFile">
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
      </a-col>

      <a-col :span="24" :lg="12">
        <a-card class="result-card" title="📝 识别结果" :loading="loading">
          <template #extra>
            <a-space>
              <a-button type="link" @click="copyResult" :disabled="!result">
                <CopyOutlined />
                <span>复制文本</span>
              </a-button>
              <a-button type="link" @click="downloadText" :disabled="!result">
                <DownloadOutlined />
                <span>下载文本</span>
              </a-button>
            </a-space>
          </template>

          <div v-if="result" class="result-content">
            <div class="result-meta">
              <a-tag color="processing">语言: {{ form.language }}</a-tag>
              <a-tag color="success">精度: {{ form.detailLevel }}</a-tag>
              <a-tag color="cyan" v-if="form.model">模型: {{ form.model }}</a-tag>
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

          <div v-else-if="error" class="result-placeholder">
            <a-result
              status="error"
              title="识别失败"
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
            <a-empty description="请先上传图片并开始识别" />
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-alert type="info" show-icon class="helper-alert" message="提示">
      <template #description>
        <p>支持多语言识别，建议使用高质量图片以获得更好效果。</p>
        <p>注意：图片的高和宽都必须大于28像素。</p>
      </template>
    </a-alert>

    <!-- 图片预览模态框 -->
    <a-modal 
      v-model:open="imageModalVisible" 
      title="图片预览" 
      width="80%"
      :footer="null"
      centered
      @after-close="resetImageTransform"
    >
      <template #extra>
        <a-space>
          <a-button size="small" @click="zoomIn">
            <PlusOutlined /> 放大
          </a-button>
          <a-button size="small" @click="zoomOut">
            <MinusOutlined /> 缩小
          </a-button>
          <a-button size="small" @click="resetImageTransform">
            <ReloadOutlined /> 重置
          </a-button>
          <a-tag>{{ Math.round(imageScale * 100) }}%</a-tag>
        </a-space>
      </template>
      <div 
        class="image-modal-content" 
        @wheel="handleWheel"
        @mousedown="startDrag"
        @mousemove="onDrag"
        @mouseup="stopDrag"
        @mouseleave="stopDrag"
      >
        <img 
          :src="imagePreview" 
          alt="图片预览" 
          class="modal-image"
          :style="imageTransformStyle"
          @dragstart.prevent
        />
      </div>
    </a-modal>
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
  DownloadOutlined,
  PlusOutlined,
  MinusOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import { getCachedModels, setCachedModels } from '../utils/modelCache'

export default {
  name: 'OCR',
  components: {
    UploadOutlined,
    HighlightOutlined,
    DeleteOutlined,
    CopyOutlined,
    DownloadOutlined,
    PlusOutlined,
    MinusOutlined,
    ReloadOutlined
  },
  data() {
    return {
      loading: false,
      loadingModels: false,
      visionModels: [],
      form: {
        language: 'auto',
        detailLevel: 'medium',
        model: ''
      },
      imageFile: null,
      imagePreview: null,
      result: null,
      error: null,
      processingTime: 0,
      imageModalVisible: false,
      // 图片缩放和拖动相关
      imageScale: 1,
      imageTranslateX: 0,
      imageTranslateY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0
    }
  },
  computed: {
    imageTransformStyle() {
      return {
        transform: `scale(${this.imageScale}) translate(${this.imageTranslateX}px, ${this.imageTranslateY}px)`,
        cursor: this.isDragging ? 'grabbing' : 'grab',
        transition: this.isDragging ? 'none' : 'transform 0.2s ease'
      }
    }
  },
  async mounted() {
    await this.loadAvailableModels()
    // 添加全局粘贴事件监听
    window.addEventListener('paste', this.handlePaste)
  },
  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('paste', this.handlePaste)
    if (this.imagePreview) {
      URL.revokeObjectURL(this.imagePreview)
    }
  },
  methods: {
    async loadAvailableModels() {
      // 先尝试从缓存读取
      const cachedModels = getCachedModels()
      if (cachedModels && cachedModels.length > 0) {
        // 筛选出视觉模型（包含 V 或 Vision 的模型）
        this.visionModels = cachedModels.filter(m => 
          m.id.includes('V') || m.id.includes('Vision') || m.id.includes('vision')
        )
        if (!this.form.model && this.visionModels.length > 0) {
          // 优先选择 GLM-4V
          const glmVisionModel = this.visionModels.find(m => m.id.includes('GLM-4V'))
          this.form.model = glmVisionModel ? glmVisionModel.id : this.visionModels[0].id
        }
        return
      }

      // 缓存不存在或过期，从后端加载
      this.loadingModels = true
      try {
        const response = await aiService.getModels()
        if (response.data.models && response.data.models.length > 0) {
          setCachedModels(response.data.models)
          // 筛选出视觉模型
          this.visionModels = response.data.models.filter(m => 
            m.id.includes('V') || m.id.includes('Vision') || m.id.includes('vision')
          )
          if (!this.form.model && this.visionModels.length > 0) {
            // 优先选择 GLM-4V
            const glmVisionModel = this.visionModels.find(m => m.id.includes('GLM-4V'))
            this.form.model = glmVisionModel ? glmVisionModel.id : this.visionModels[0].id
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
    /**
     * 处理文件上传前的验证
     * @param {File} file - 用户选择的文件
     * @returns {boolean} - 是否继续上传流程
     */
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

      // 检查图片尺寸
      const img = new Image();
      const objectUrl = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(objectUrl);
        if (img.width < 28 || img.height < 28) {
          message.error('图片尺寸太小，请上传高和宽都大于28像素的图片');
          return;
        }

        // 尺寸检查通过，继续处理
        this.processImageFile(file);
      };

      img.onerror = () => {
        URL.revokeObjectURL(objectUrl);
        message.error('无法读取图片文件');
      };

      img.src = objectUrl;

      // 返回false阻止自动上传，我们会在尺寸检查通过后手动处理
      return false;
    },

    /**
     * 处理通过验证的图片文件
     * @param {File} file - 通过验证的图片文件
     */
    processImageFile(file) {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }

      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
      this.result = null
      this.error = null
    },

    /**
     * 执行OCR文字识别
     * @returns {Promise<void>}
     */
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
        if (this.form.model) {
          formData.append('model', this.form.model)
        }

        const response = await aiService.ocr(formData)

        this.processingTime = Date.now() - startTime

        if (response.data.success) {
          this.result = response.data
          message.success('文字识别完成')
        } else {
          // 显示详细的错误信息
          const errorMsg = response.data.error || '识别失败'
          this.error = errorMsg
          message.error(errorMsg, 5)
        }
      } catch (error) {
        console.error('识别请求失败:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.error || '网络请求失败'
        this.error = errorMsg
        message.error(errorMsg, 5)
      } finally {
        this.loading = false
      }
    },

    /**
     * 清除已上传的图片和相关数据
     */
    clearImage() {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }
      this.imageFile = null
      this.imagePreview = null
      this.result = null
      this.error = null
    },

    /**
     * 复制识别结果到剪贴板
     * @returns {Promise<void>}
     */
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

    /**
     * 下载识别结果为文本文件
     */
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

    /**
     * 格式化文件大小显示
     * @param {number} bytes - 文件大小（字节）
     * @returns {string} - 格式化后的文件大小
     */
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
    },

    /**
     * 处理粘贴事件
     * @param {ClipboardEvent} event - 粘贴事件
     */
    handlePaste(event) {
      const items = event.clipboardData?.items
      if (!items) return

      // 查找图片数据
      for (let i = 0; i < items.length; i++) {
        const item = items[i]
        if (item.type.indexOf('image') !== -1) {
          event.preventDefault()
          const file = item.getAsFile()
          if (file) {
            // 使用与上传相同的验证逻辑
            this.validateAndProcessImage(file)
            message.success('已粘贴图片')
          }
          break
        }
      }
    },

    /**
     * 验证并处理图片文件
     * @param {File} file - 图片文件
     */
    validateAndProcessImage(file) {
      // 文件大小验证
      if (file.size > 10 * 1024 * 1024) {
        message.error('文件大小不能超过 10MB')
        return
      }

      // 文件类型验证
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 JPG、PNG、GIF、WebP 格式的图片')
        return
      }

      // 检查图片尺寸
      const img = new Image()
      const objectUrl = URL.createObjectURL(file)

      img.onload = () => {
        URL.revokeObjectURL(objectUrl)
        if (img.width < 28 || img.height < 28) {
          message.error('图片尺寸太小，请上传高和宽都大于28像素的图片')
          return
        }

        // 尺寸检查通过，继续处理
        this.processImageFile(file)
      }

      img.onerror = () => {
        URL.revokeObjectURL(objectUrl)
        message.error('无法读取图片文件')
      }

      img.src = objectUrl
    },

    /**
     * 显示图片预览模态框
     */
    showImageModal() {
      this.imageModalVisible = true
    },

    /**
     * 放大图片
     */
    zoomIn() {
      this.imageScale = Math.min(this.imageScale + 0.2, 5)
    },

    /**
     * 缩小图片
     */
    zoomOut() {
      this.imageScale = Math.max(this.imageScale - 0.2, 0.2)
    },

    /**
     * 重置图片变换
     */
    resetImageTransform() {
      this.imageScale = 1
      this.imageTranslateX = 0
      this.imageTranslateY = 0
      this.isDragging = false
    },

    /**
     * 处理鼠标滚轮事件（缩放）
     */
    handleWheel(event) {
      event.preventDefault()
      const delta = event.deltaY > 0 ? -0.1 : 0.1
      this.imageScale = Math.max(0.2, Math.min(5, this.imageScale + delta))
    },

    /**
     * 开始拖动
     */
    startDrag(event) {
      if (event.button !== 0) return // 只响应左键
      this.isDragging = true
      this.dragStartX = event.clientX - this.imageTranslateX
      this.dragStartY = event.clientY - this.imageTranslateY
    },

    /**
     * 拖动中
     */
    onDrag(event) {
      if (!this.isDragging) return
      this.imageTranslateX = event.clientX - this.dragStartX
      this.imageTranslateY = event.clientY - this.dragStartY
    },

    /**
     * 停止拖动
     */
    stopDrag() {
      this.isDragging = false
    }
  }
}
</script>

<style scoped>
.ocr {
  padding: 20px;
}

.form-card {
  border-radius: 8px;
  height: 100%;
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
  margin-bottom: 8px;
}

.paste-tip {
  color: #1677ff;
  font-size: 13px;
  font-weight: 500;
  margin-top: 8px;
}

.paste-tip strong {
  background-color: #f0f5ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: 'Monaco', 'Consolas', monospace;
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

.clickable-image {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.clickable-image:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.image-info {
  margin-top: 12px;
}

.image-info p {
  margin: 4px 0;
  color: #666;
  font-size: 12px;
}

.result-card {
  border-radius: 8px;
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

.result-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.error-alert {
  margin-top: 16px;
}

.helper-alert {
  margin-top: 20px;
}

:deep(.el-upload) {
  width: 100%;
}

:deep(.el-upload-dragger) {
  width: 100%;
}

.image-modal-content {
  text-align: center;
  padding: 20px;
  overflow: hidden;
  position: relative;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border-radius: 8px;
}

.modal-image {
  max-width: 100%;
  max-height: 70vh;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  user-select: none;
  transform-origin: center center;
}
</style>
