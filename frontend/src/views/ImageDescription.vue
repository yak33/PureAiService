<template>
  <div class="image-description">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="🎨 图像描述生成">
          <a-form :model="form" layout="vertical">
            <a-row :gutter="20">
              <a-col :span="24" :md="12">
                <a-form-item label="生成模型">
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
              </a-col>

              <a-col :span="24" :md="12">
                <a-form-item label="描述风格">
                  <a-select v-model:value="form.style" placeholder="选择描述风格">
                    <a-select-option value="realistic">写实风格</a-select-option>
                    <a-select-option value="artistic">艺术风格</a-select-option>
                    <a-select-option value="cartoon">卡通风格</a-select-option>
                  </a-select>
                </a-form-item>
              </a-col>
            </a-row>

            <a-form-item label="生成数量">
              <a-space>
                <a-input-number v-model:value="form.n" :min="1" :max="5" />
                <span class="form-tip">最多可生成5个不同的描述</span>
              </a-space>
            </a-form-item>

            <a-form-item label="基础描述">
              <a-textarea v-model:value="form.prompt" :rows="4" placeholder="请输入您想要的图像基础描述，例如：一只可爱的小猫在花园里玩耍"
                :maxlength="500" show-count :auto-size="{ minRows: 4, maxRows: 10 }" />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button type="primary" @click="generateDescription" :loading="loading"
                  :disabled="!form.prompt.trim()">
                  <HighlightOutlined />
                  <span>生成描述</span>
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
        <a-card class="result-card" title="✨ 生成的图像描述" :loading="loading">
          <template #extra>
            <a-button type="link" @click="copyAllResults" :disabled="!results.length">
              <CopyOutlined />
              <span>复制全部</span>
            </a-button>
          </template>

          <div v-if="results.length" class="results-container">
            <div class="result-meta">
              <a-tag color="processing">风格: {{ getStyleLabel(form.style) }}</a-tag>
              <a-tag color="success">模型: {{ currentModel }}</a-tag>
              <a-tag color="warning">数量: {{ results.length }}</a-tag>
            </div>

            <div v-for="(result, index) in results" :key="index" class="description-item">
              <div class="description-header">
                <h4>描述 {{ index + 1 }}</h4>
                <div class="description-actions">
                  <a-button type="link" size="small" @click="copyDescription(result.description)">
                    <CopyOutlined />
                    <span>复制</span>
                  </a-button>
                  <a-button type="link" size="small" @click="useAsPrompt(result.description)">
                    <ReloadOutlined />
                    <span>作为新输入</span>
                  </a-button>
                </div>
              </div>
              <div class="description-content" v-html="renderMarkdown(result.description)"></div>
            </div>

            <div class="usage-tip">
              <a-alert type="info" show-icon :closable="false">
                <template #message>使用提示</template>
                <template #description>
                  <p>生成的详细描述可以用于：</p>
                  <ul>
                    <li>🎨 AI图像生成工具（如Midjourney、DALL-E、Stable Diffusion）</li>
                    <li>📝 创意写作和故事创作</li>
                    <li>🎯 广告文案和营销素材</li>
                    <li>🎬 影视剧本和分镜头描述</li>
                  </ul>
                </template>
              </a-alert>
            </div>
          </div>

          <div v-else class="result-placeholder">
            <a-empty description="请先生成图像描述" />
          </div>
        </a-card>

        <a-alert v-if="error" type="error" show-icon class="error-alert" :message="error" />
      </a-col>
    </a-row>

    <a-card class="examples-card" title="💡 输入示例">
      <div class="examples-container">
        <div class="example-category">
          <h4>人物场景</h4>
          <div class="example-tags">
            <a-tag v-for="example in personExamples" :key="example" class="example-tag" @click="useExample(example)">
              {{ example }}
            </a-tag>
          </div>
        </div>

        <div class="example-category">
          <h4>自然风景</h4>
          <div class="example-tags">
            <a-tag v-for="example in natureExamples" :key="example" class="example-tag" @click="useExample(example)">
              {{ example }}
            </a-tag>
          </div>
        </div>

        <div class="example-category">
          <h4>物品静物</h4>
          <div class="example-tags">
            <a-tag v-for="example in objectExamples" :key="example" class="example-tag" @click="useExample(example)">
              {{ example }}
            </a-tag>
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
  HighlightOutlined,
  DeleteOutlined,
  CopyOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import { getCachedModels, setCachedModels } from '../utils/modelCache'
import eventBus, { EVENT_MODELS_UPDATED } from '../utils/eventBus'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

export default {
  name: 'ImageDescription',
  components: {
    HighlightOutlined,
    DeleteOutlined,
    CopyOutlined,
    ReloadOutlined
  },
  data() {
    return {
      loading: false,
      loadingModels: false,
      availableModels: [],
      form: {
        prompt: '',
        model: '',
        style: 'realistic',
        n: 1
      },
      results: [],
      error: null,
      currentModel: '',
      personExamples: [
        '一位年轻女性在咖啡店里阅读',
        '小孩在公园里放风筝',
        '老人在花园里浇花',
        '商务人士在办公室工作'
      ],
      natureExamples: [
        '夕阳下的海滩',
        '雪山脚下的小村庄',
        '春天的樱花树',
        '雨后的森林'
      ],
      objectExamples: [
        '桌上的一杯热咖啡',
        '书架上的古老书籍',
        '窗台上的绿色植物',
        '厨房里的美味蛋糕'
      ]
    }
  },
  async mounted() {
    await this.loadAvailableModels()
    // 监听模型更新事件
    eventBus.on(EVENT_MODELS_UPDATED, this.handleModelsUpdated)
  },
  beforeUnmount() {
    // 移除事件监听
    eventBus.off(EVENT_MODELS_UPDATED, this.handleModelsUpdated)
  },
  methods: {
    async loadAvailableModels() {
      // 先尝试从缓存读取
      const cachedModels = getCachedModels()
      if (cachedModels && cachedModels.length > 0) {
        this.availableModels = cachedModels
        if (!this.form.model && this.availableModels.length > 0) {
          // 优先选择GLM模型
          const glmModel = this.availableModels.find(m => m.id.includes('GLM'))
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
          setCachedModels(this.availableModels)
          if (!this.form.model && this.availableModels.length > 0) {
            // 优先选择GLM模型
            const glmModel = this.availableModels.find(m => m.id.includes('GLM'))
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

    async generateDescription() {
      if (!this.form.prompt.trim()) {
        message.warning('请输入基础描述')
        return
      }

      this.loading = true
      this.results = []
      this.error = null

      try {
        const requestData = {
          prompt: this.form.prompt,
          model: this.form.model,
          style: this.form.style,
          n: this.form.n
        }

        const response = await aiService.generateImageDescription(requestData)

        if (response.data.success) {
          this.results = response.data.descriptions
          this.currentModel = response.data.model
          message.success('图像描述生成完成')
        } else {
          this.error = response.data.error || '生成失败'
          message.error('生成失败')
        }
      } catch (error) {
        console.error('生成请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        message.error('生成请求失败')
      } finally {
        this.loading = false
      }
    },

    clearForm() {
      this.form.prompt = ''
      this.results = []
      this.error = null
    },

    async copyDescription(description) {
      try {
        await navigator.clipboard.writeText(description)
        message.success('描述已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        message.error('复制失败')
      }
    },

    async copyAllResults() {
      if (this.results.length === 0) return

      const allDescriptions = this.results
        .map((result, index) => `描述 ${index + 1}:\n${result.description}`)
        .join('\n\n---\n\n')

      try {
        await navigator.clipboard.writeText(allDescriptions)
        message.success('所有描述已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        message.error('复制失败')
      }
    },

    useAsPrompt(description) {
      this.form.prompt = description
      message.success('已将描述设为新的输入')
    },

    useExample(example) {
      this.form.prompt = example
      message.success('已使用示例作为输入')
    },

    getStyleLabel(style) {
      const labels = {
        realistic: '写实风格',
        artistic: '艺术风格',
        cartoon: '卡通风格'
      }
      return labels[style] || style
    },

    renderMarkdown(content) {
      if (!content) return ''
      marked.setOptions({
        highlight: function (code, lang) {
          if (lang && hljs.getLanguage(lang)) {
            try {
              return hljs.highlight(code, { language: lang }).value
            } catch (err) {
              console.error('代码高亮失败:', err)
            }
          }
          return hljs.highlightAuto(code).value
        },
        breaks: true,
        gfm: true
      })
      return marked.parse(content)
    },

    /**
     * 处理模型更新事件
     * 当模型配置被修改时，重新加载模型列表
     */
    async handleModelsUpdated(data) {
      console.log('收到模型更新通知:', data)
      message.info('模型列表已更新，正在刷新...', 2)

      // 重新加载模型列表
      await this.loadAvailableModels()

      // 如果当前选择的模型不在新的模型列表中，自动切换到第一个
      if (this.form.model && !this.availableModels.some(m => m.id === this.form.model)) {
        if (this.availableModels.length > 0) {
          // 优先选择GLM模型
          const glmModel = this.availableModels.find(m => m.id.includes('GLM'))
          this.form.model = glmModel ? glmModel.id : this.availableModels[0].id
          message.warning('原模型已被移除，已自动切换到: ' + this.form.model, 3)
        } else {
          this.form.model = ''
          message.warning('当前没有可用模型，请先在模型管理页面配置', 4)
        }
      }
    }
  }
}
</script>

<style scoped>
.image-description {
  padding: 20px;
}

.form-card {
  border-radius: 8px;
  height: 100%;
}

.form-tip {
  color: #909399;
  font-size: 12px;
}

.result-card {
  height: 100%;
}

.results-container {
  padding: 10px 0;
}

.result-meta {
  margin-bottom: 20px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.result-meta :deep(.ant-tag) {
  margin-right: 0;
}

.description-item {
  margin-bottom: 24px;
  border: 1px solid #e4e4e4;
  border-radius: 8px;
  overflow: hidden;
}

.description-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-bottom: 1px solid #e4e4e4;
}

.description-header h4 {
  margin: 0;
  color: #333;
  font-size: 14px;
}

.description-actions {
  display: flex;
  gap: 8px;
}

.description-content {
  padding: 16px;
}

/* Markdown 样式 */
.description-content :deep(h1),
.description-content :deep(h2),
.description-content :deep(h3),
.description-content :deep(h4),
.description-content :deep(h5),
.description-content :deep(h6) {
  margin: 16px 0 8px;
  font-weight: 600;
  line-height: 1.25;
}

.description-content :deep(h1) {
  font-size: 1.5em;
}

.description-content :deep(h2) {
  font-size: 1.3em;
}

.description-content :deep(h3) {
  font-size: 1.1em;
}

.description-content :deep(p) {
  margin: 8px 0;
  line-height: 1.6;
}

.description-content :deep(ul),
.description-content :deep(ol) {
  padding-left: 1.5em;
  margin: 8px 0;
}

.description-content :deep(li) {
  margin: 4px 0;
  line-height: 1.6;
}

.description-content :deep(code) {
  background-color: rgba(27, 31, 35, 0.05);
  border-radius: 3px;
  font-size: 85%;
  padding: 0.2em 0.4em;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.description-content :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  overflow: auto;
  margin: 8px 0;
  border: 1px solid #e9ecef;
}

.description-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  font-size: 100%;
  display: block;
  white-space: pre;
  line-height: 1.5;
}

.description-content :deep(blockquote) {
  border-left: 4px solid #dfe2e5;
  padding: 0 0.8em;
  color: #6a737d;
  margin: 8px 0;
}

.description-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 8px 0;
}

.description-content :deep(table th),
.description-content :deep(table td) {
  border: 1px solid #dfe2e5;
  padding: 6px 10px;
}

.description-content :deep(table th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

.description-content :deep(hr) {
  border: none;
  border-top: 1px solid #e9ecef;
  margin: 12px 0;
}

.description-content :deep(a) {
  color: #0969da;
  text-decoration: none;
}

.description-content :deep(a:hover) {
  text-decoration: underline;
}

.description-content :deep(strong) {
  font-weight: 600;
}

.description-content :deep(em) {
  font-style: italic;
}

.result-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 240px;
}

.usage-tip {
  margin-top: 20px;
}

.usage-tip ul {
  margin: 8px 0 0 0;
  padding-left: 16px;
}

.usage-tip li {
  margin: 4px 0;
}

.error-alert {
  margin-top: 20px;
}

.examples-card {
  margin-top: 20px;
}

.examples-container {
  padding: 10px 0;
}

.example-category {
  margin-bottom: 20px;
}

.example-category h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 14px;
}

.example-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.example-tag {
  cursor: pointer;
  transition: all 0.3s ease;
}

.example-tag:hover {
  background-color: #1677ff;
  color: white;
  transform: translateY(-2px);
}
</style>
