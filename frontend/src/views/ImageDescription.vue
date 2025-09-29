<template>
  <div class="image-description">
    <a-row :gutter="16">
      <a-col :span="24" :lg="12">
        <a-card class="form-card" title="🎨 图像描述生成">
          <a-form :model="form" layout="vertical">
            <a-row :gutter="20">
              <a-col :span="24" :md="12">
                <a-form-item label="生成模型">
                  <a-select v-model:value="form.model" placeholder="选择AI模型">
                    <a-select-option value="zai-org/GLM-4.5">GLM-4.5 (推荐)</a-select-option>
                    <a-select-option value="moonshotai/Kimi-K2-Instruct-0905">Kimi-K2</a-select-option>
                  </a-select>
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
              <a-textarea
                v-model:value="form.prompt"
                :rows="4"
                placeholder="请输入您想要的图像基础描述，例如：一只可爱的小猫在花园里玩耍"
                :maxlength="500"
                show-count
                :auto-size="{ minRows: 4, maxRows: 10 }"
              />
            </a-form-item>

            <a-form-item>
              <a-space>
                <a-button
                  type="primary"
                  @click="generateDescription"
                  :loading="loading"
                  :disabled="!form.prompt.trim()"
                >
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

            <div
              v-for="(result, index) in results"
              :key="index"
              class="description-item"
            >
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
              <div class="description-content">
                <pre>{{ result.description }}</pre>
              </div>
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

        <a-alert
          v-if="error"
          type="error"
          show-icon
          class="error-alert"
          :message="error"
        />
      </a-col>
    </a-row>

    <a-card class="examples-card" title="💡 输入示例">
      <div class="examples-container">
        <div class="example-category">
          <h4>人物场景</h4>
          <div class="example-tags">
            <a-tag
              v-for="example in personExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
              {{ example }}
            </a-tag>
          </div>
        </div>

        <div class="example-category">
          <h4>自然风景</h4>
          <div class="example-tags">
            <a-tag
              v-for="example in natureExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
              {{ example }}
            </a-tag>
          </div>
        </div>

        <div class="example-category">
          <h4>物品静物</h4>
          <div class="example-tags">
            <a-tag
              v-for="example in objectExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
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
      form: {
        prompt: '',
        model: 'zai-org/GLM-4.5',
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
  methods: {
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

.description-content pre {
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