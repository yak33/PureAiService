<template>
  <div class="image-edit">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="✨ AI 图片编辑">
          <a-form :model="form" layout="vertical">
            <a-form-item label="上传图片">
              <a-upload-dragger name="file" :show-upload-list="false" :before-upload="handleBeforeUpload"
                accept="image/*" @paste.native="handlePaste">
                <div v-if="!imageFile" class="upload-area">
                  <PictureOutlined class="upload-icon" />
                  <p class="upload-text">将图片拖拽到此处，或<em>点击上传</em></p>
                  <p class="upload-tip">支持 JPG、PNG、WebP 格式，文件大小不超过 10MB</p>
                  <p class="paste-tip">📋 也可以直接 <strong>Ctrl+V</strong> 粘贴图片</p>
                </div>
                <div v-else class="image-preview">
                  <img :src="imagePreview" alt="原始图片" @click.stop="showImageModal" class="clickable-image" />
                  <div class="image-info">
                    <p>{{ imageFile.name }}</p>
                    <p>{{ formatFileSize(imageFile.size) }}</p>
                  </div>
                </div>
              </a-upload-dragger>
            </a-form-item>

            <a-form-item label="AI模型">
              <a-select v-model:value="form.model" placeholder="选择AI模型" :loading="loadingModels" show-search
                :filter-option="filterOption">
                <a-select-option v-for="model in availableModels" :key="model.id" :value="model.id">
                  {{ model.id }}
                </a-select-option>
              </a-select>
              <div v-if="!loadingModels && availableModels.length === 0" style="margin-top: 8px;">
                <a-alert type="warning" message="请先在模型管理页面配置可用模型" show-icon />
              </div>
            </a-form-item>

            <a-form-item label="编辑指令">
              <a-textarea v-model:value="form.instruction" :rows="4"
                placeholder="描述你想要对图片进行的修改，例如：&#10;- 把背景改成海滩&#10;- 给人物添加一顶帽子&#10;- 将天空变成日落效果&#10;- 去掉图片中的文字"
                :maxlength="500" show-count :auto-size="{ minRows: 4, maxRows: 8 }" />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button type="primary" @click="editImage" :loading="loading" :disabled="!canEdit">
                  <EditOutlined />
                  <span>开始编辑</span>
                </a-button>
                <a-button @click="clearForm" v-if="imageFile || form.instruction">
                  <DeleteOutlined />
                  <span>清空内容</span>
                </a-button>
              </a-space>
            </a-form-item>
          </a-form>

          <a-divider>快速指令模板</a-divider>
          <div class="quick-templates">
            <a-tag v-for="template in templates" :key="template" class="template-tag" @click="useTemplate(template)">
              {{ template }}
            </a-tag>
          </div>
        </a-card>
      </a-col>

      <a-col :span="24" :lg="12">
        <a-card class="result-card" title="🎨 编辑结果" :loading="loading">
          <template #extra>
            <a-space>
              <a-button type="link" @click="downloadImage" :disabled="!editedImageUrl">
                <DownloadOutlined />
                <span>下载图片</span>
              </a-button>
              <a-button type="link" @click="compareImages" :disabled="!editedImageUrl">
                <EyeOutlined />
                <span>对比查看</span>
              </a-button>
            </a-space>
          </template>

          <div v-if="editedImageUrl" class="result-content">
            <div class="result-meta">
              <a-tag color="success">编辑成功</a-tag>
              <a-tag color="processing">模型: {{ form.model || 'Qwen-Image-Edit-2509' }}</a-tag>
              <a-tag color="cyan" v-if="result.seed">
                随机种子: {{ result.seed }}
              </a-tag>
              <a-tag color="warning" v-if="result.timings">
                耗时: {{ result.timings.inference }}ms
              </a-tag>
            </div>

            <div class="edited-image-container">
              <img :src="editedImageUrl" alt="编辑后的图片" class="edited-image" />
            </div>

            <div class="result-actions">
              <a-button type="primary" @click="useAsNewSource" block>
                <ReloadOutlined />
                <span>将此图片作为新的编辑源</span>
              </a-button>
            </div>
          </div>

          <div v-else-if="error" class="result-placeholder">
            <a-result status="error" title="编辑失败" :sub-title="error">
              <template #extra>
                <a-button type="primary" @click="error = null">
                  知道了
                </a-button>
              </template>
            </a-result>
          </div>

          <div v-else class="result-placeholder">
            <a-empty description="请上传图片并输入编辑指令" />
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-card class="info-card" title="💡 使用提示">
      <a-row :gutter="16">
        <a-col :span="24" :md="8">
          <div class="tip-section">
            <h4>🎯 支持的编辑类型</h4>
            <ul>
              <li>更换背景场景</li>
              <li>添加或移除物体</li>
              <li>修改颜色和光线</li>
              <li>调整风格和滤镜</li>
            </ul>
          </div>
        </a-col>
        <a-col :span="24" :md="8">
          <div class="tip-section">
            <h4>✍️ 编写指令技巧</h4>
            <ul>
              <li>使用清晰具体的描述</li>
              <li>一次只修改一个主要方面</li>
              <li>描述期望的结果而非过程</li>
              <li>可以指定风格和氛围</li>
            </ul>
          </div>
        </a-col>
        <a-col :span="24" :md="8">
          <div class="tip-section">
            <h4>⚡ 最佳实践</h4>
            <ul>
              <li>使用高质量的源图片</li>
              <li>避免过于复杂的指令</li>
              <li>可以多次编辑迭代优化</li>
              <li>保存满意的编辑结果</li>
            </ul>
          </div>
        </a-col>
      </a-row>
    </a-card>

    <!-- 图片对比模态框 -->
    <a-modal v-model:open="compareModalVisible" title="图片对比" width="80%" :footer="null">
      <div class="compare-container">
        <div class="compare-image">
          <h4>原图</h4>
          <img :src="imagePreview" alt="原图" />
        </div>
        <div class="compare-divider"></div>
        <div class="compare-image">
          <h4>编辑后</h4>
          <img :src="editedImageUrl" alt="编辑后" />
        </div>
      </div>
    </a-modal>

    <!-- 图片预览模态框 -->
    <a-modal v-model:open="imageModalVisible" title="图片预览" width="80%" :footer="null" centered
      @after-close="resetImageTransform">
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
      <div class="image-modal-content" @wheel="handleWheel" @mousedown="startDrag" @mousemove="onDrag"
        @mouseup="stopDrag" @mouseleave="stopDrag">
        <img :src="imagePreview" alt="图片预览" class="modal-image" :style="imageTransformStyle" @dragstart.prevent />
      </div>
    </a-modal>
  </div>
</template>

<script>
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import {
  PictureOutlined,
  EditOutlined,
  DeleteOutlined,
  DownloadOutlined,
  EyeOutlined,
  ReloadOutlined,
  PlusOutlined,
  MinusOutlined
} from '@ant-design/icons-vue'
import { getCachedModels, setCachedModels } from '../utils/modelCache'
import eventBus, { EVENT_MODELS_UPDATED } from '../utils/eventBus'

export default {
  name: 'ImageEdit',
  components: {
    PictureOutlined,
    EditOutlined,
    DeleteOutlined,
    DownloadOutlined,
    EyeOutlined,
    ReloadOutlined,
    PlusOutlined,
    MinusOutlined
  },
  data() {
    return {
      loading: false,
      loadingModels: false,
      availableModels: [],
      form: {
        instruction: '',
        model: ''
      },
      imageFile: null,
      imagePreview: null,
      editedImage: null,
      editedImageDirectUrl: null,  // 存储直接 URL
      result: null,
      error: null,
      compareModalVisible: false,
      imageModalVisible: false,
      // 图片缩放和拖动相关
      imageScale: 1,
      imageTranslateX: 0,
      imageTranslateY: 0,
      isDragging: false,
      dragStartX: 0,
      dragStartY: 0,
      templates: [
        '把背景改成海滩',
        '添加一顶帽子',
        '改成黑白照片',
        '添加日落效果',
        '去除背景',
        '改成卡通风格',
        '添加雪花效果',
        '改成夜景'
      ]
    }
  },
  async mounted() {
    await this.loadAvailableModels()
    // 添加全局粘贴事件监听
    window.addEventListener('paste', this.handlePaste)

    // 监听模型更新事件
    eventBus.on(EVENT_MODELS_UPDATED, this.handleModelsUpdated)
  },
  computed: {
    canEdit() {
      return this.imageFile && this.form.instruction.trim()
    },
    imageTransformStyle() {
      return {
        transform: `scale(${this.imageScale}) translate(${this.imageTranslateX}px, ${this.imageTranslateY}px)`,
        cursor: this.isDragging ? 'grabbing' : 'grab',
        transition: this.isDragging ? 'none' : 'transform 0.2s ease'
      }
    },
    editedImageUrl() {
      // 优先使用直接 URL（浏览器可以访问）
      if (this.editedImageDirectUrl) {
        return this.editedImageDirectUrl
      }

      // 如果有 base64 数据，使用 base64
      if (!this.editedImage) return null

      // 如果已经是完整的 data URL
      if (this.editedImage.startsWith('data:image')) {
        return this.editedImage
      }
      // 如果是纯 base64，添加前缀
      return `data:image/jpeg;base64,${this.editedImage}`
    }
  },
  methods: {
    async loadAvailableModels() {
      // 先尝试从缓存读取
      const cachedModels = getCachedModels()
      if (cachedModels && cachedModels.length > 0) {
        this.availableModels = cachedModels
        if (!this.form.model && this.availableModels.length > 0) {
          // 优先选择包含编辑功能的模型
          const editModel = this.availableModels.find(m =>
            m.id.includes('Edit') || m.id.includes('edit')
          )
          this.form.model = editModel ? editModel.id : this.availableModels[0].id
        }
        return
      }

      // 缓存不存在或过期，从后端加载
      this.loadingModels = true
      try {
        const response = await aiService.getModels()
        if (response.data.models && response.data.models.length > 0) {
          this.availableModels = response.data.models
          setCachedModels(this.availableModels)
          if (!this.form.model && this.availableModels.length > 0) {
            // 优先选择包含编辑功能的模型
            const editModel = this.availableModels.find(m =>
              m.id.includes('Edit') || m.id.includes('edit')
            )
            this.form.model = editModel ? editModel.id : this.availableModels[0].id
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
    handleBeforeUpload(file) {
      if (file.size > 10 * 1024 * 1024) {
        message.error('文件大小不能超过 10MB')
        return false
      }

      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 JPG、PNG、WebP 格式的图片')
        return false
      }

      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }

      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
      this.editedImage = null
      this.result = null
      this.error = null

      return false
    },

    async editImage() {
      if (!this.canEdit) {
        message.warning('请上传图片并输入编辑指令')
        return
      }

      this.loading = true
      this.editedImage = null
      this.editedImageDirectUrl = null
      this.error = null

      try {
        const formData = new FormData()
        formData.append('file', this.imageFile)
        formData.append('instruction', this.form.instruction)
        if (this.form.model) {
          formData.append('model', this.form.model)
        }

        const response = await aiService.editImage(formData)

        if (response.data.success) {
          this.result = response.data

          // 优先使用直接 URL（浏览器可以访问）
          if (response.data.image_url) {
            this.editedImageDirectUrl = response.data.image_url
          }

          // 如果有 base64 数据也保存（作为备用）
          if (response.data.edited_image) {
            this.editedImage = response.data.edited_image
          }

          message.success('图片编辑完成！')
        } else {
          // 显示详细的错误信息
          let errorMsg = response.data.error || '编辑失败'

          // 如果是内容敏感错误，追加中文提示
          if (errorMsg.includes('prohibited') || errorMsg.includes('sensitive')) {
            errorMsg = errorMsg + '\n\n提示：图片或指令包含敏感内容，请调整后重试'
            message.error('图片或指令包含敏感内容，请调整后重试', 5)
          } else {
            message.error(errorMsg, 5)
          }

          this.error = errorMsg
        }
      } catch (error) {
        console.error('编辑请求失败:', error)
        const errorMsg = error.response?.data?.detail || error.response?.data?.error || '网络请求失败'
        this.error = errorMsg
        message.error(errorMsg, 5)
      } finally {
        this.loading = false
      }
    },

    clearForm() {
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }
      this.imageFile = null
      this.imagePreview = null
      this.form.instruction = ''
      this.editedImage = null
      this.editedImageDirectUrl = null
      this.result = null
      this.error = null
    },

    useTemplate(template) {
      this.form.instruction = template
      message.success('已使用模板')
    },

    downloadImage() {
      if (!this.editedImageUrl) return

      const link = document.createElement('a')
      link.href = this.editedImageUrl
      link.download = `edited_image_${Date.now()}.png`
      link.target = '_blank'
      link.click()

      message.success('图片已下载')
    },

    compareImages() {
      if (!this.editedImageUrl || !this.imagePreview) return
      this.compareModalVisible = true
    },

    useAsNewSource() {
      if (!this.editedImageUrl) return

      // 将编辑后的图片转换为 Blob，然后创建新的 File 对象
      fetch(this.editedImageUrl)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], `edited_${Date.now()}.png`, { type: 'image/png' })

          if (this.imagePreview) {
            URL.revokeObjectURL(this.imagePreview)
          }

          this.imageFile = file
          this.imagePreview = URL.createObjectURL(file)
          this.editedImage = null
          this.editedImageDirectUrl = null
          this.result = null
          this.form.instruction = ''

          message.success('已将编辑后的图片设为新的编辑源')
        })
        .catch(error => {
          console.error('转换图片失败:', error)
          message.error('操作失败')
        })
    },

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
      const allowedTypes = ['image/jpeg', 'image/png', 'image/webp']
      if (!allowedTypes.includes(file.type)) {
        message.error('只支持 JPG、PNG、WebP 格式的图片')
        return
      }

      // 处理图片
      if (this.imagePreview) {
        URL.revokeObjectURL(this.imagePreview)
      }

      this.imageFile = file
      this.imagePreview = URL.createObjectURL(file)
      this.editedImage = null
      this.editedImageDirectUrl = null
      this.result = null
      this.error = null
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
      if (this.form.model && !this.availableModels.some(m => m.id === this.form.model)) {
        if (this.availableModels.length > 0) {
          // 优先选择包含编辑功能的模型
          const editModel = this.availableModels.find(m =>
            m.id.includes('Edit') || m.id.includes('edit')
          )
          this.form.model = editModel ? editModel.id : this.availableModels[0].id
          message.warning('原模型已被移除，已自动切换到: ' + this.form.model, 3)
        } else {
          this.form.model = ''
          message.warning('当前没有可用模型，请先在模型管理页面配置', 4)
        }
      }
    }
  },

  beforeUnmount() {
    // 移除事件监听
    window.removeEventListener('paste', this.handlePaste)
    eventBus.off(EVENT_MODELS_UPDATED, this.handleModelsUpdated)

    if (this.imagePreview) {
      URL.revokeObjectURL(this.imagePreview)
    }
  }
}
</script>

<style scoped>
.image-edit {
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
  margin-top: 12px;
}

.upload-text em {
  color: #1677ff;
  font-style: normal;
  margin-left: 4px;
}

.upload-tip {
  color: #909399;
  font-size: 12px;
  margin-top: 8px;
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

.quick-templates {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.template-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.template-tag:hover {
  background-color: #1677ff;
  color: white;
  transform: translateY(-2px);
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

.edited-image-container {
  text-align: center;
  margin-bottom: 16px;
}

.edited-image {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.result-actions {
  margin-top: 16px;
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

.info-card {
  margin-top: 20px;
  border-radius: 8px;
}

.tip-section {
  margin-bottom: 16px;
}

.tip-section h4 {
  color: #333;
  font-size: 14px;
  margin-bottom: 8px;
}

.tip-section ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
  font-size: 13px;
}

.tip-section li {
  margin: 4px 0;
}

.compare-container {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.compare-image {
  flex: 1;
  text-align: center;
}

.compare-image h4 {
  margin-bottom: 12px;
  color: #333;
}

.compare-image img {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.compare-divider {
  width: 2px;
  background: linear-gradient(to bottom, #e4e4e4, #1677ff, #e4e4e4);
  align-self: stretch;
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

@media (max-width: 768px) {
  .compare-container {
    flex-direction: column;
  }

  .compare-divider {
    width: 100%;
    height: 2px;
  }
}
</style>
