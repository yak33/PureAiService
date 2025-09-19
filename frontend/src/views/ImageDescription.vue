<template>
  <div class="image-description">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🎨 图像描述生成</span>
        </div>
      </template>
      
      <el-form :model="form" label-width="120px">
        <el-form-item label="生成模型">
          <el-select v-model="form.model" placeholder="选择AI模型">
            <el-option label="GLM-4.5 (推荐)" value="zai-org/GLM-4.5" />
            <el-option label="Kimi-K2" value="moonshotai/Kimi-K2-Instruct-0905" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述风格">
          <el-select v-model="form.style" placeholder="选择描述风格">
            <el-option label="写实风格" value="realistic" />
            <el-option label="艺术风格" value="artistic" />
            <el-option label="卡通风格" value="cartoon" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="生成数量">
          <el-input-number v-model="form.n" :min="1" :max="5" />
          <span class="form-tip">最多可生成5个不同的描述</span>
        </el-form-item>
        
        <el-form-item label="基础描述">
          <el-input
            v-model="form.prompt"
            type="textarea"
            :rows="4"
            placeholder="请输入您想要的图像基础描述，例如：一只可爱的小猫在花园里玩耍"
            show-word-limit
            maxlength="500"
          />
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="generateDescription"
            :loading="loading"
            :disabled="!form.prompt.trim()"
          >
            <el-icon><MagicStick /></el-icon>
            生成描述
          </el-button>
          <el-button @click="clearForm">
            <el-icon><Delete /></el-icon>
            清空内容
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card v-if="results && results.length > 0" class="result-card">
      <template #header>
        <div class="card-header">
          <span>✨ 生成的图像描述</span>
          <el-button
            type="text"
            @click="copyAllResults"
            :icon="DocumentCopy"
          >
            复制全部
          </el-button>
        </div>
      </template>
      
      <div class="results-container">
        <div class="result-meta">
          <el-tag type="info">风格: {{ getStyleLabel(form.style) }}</el-tag>
          <el-tag type="success">模型: {{ currentModel }}</el-tag>
          <el-tag type="warning">数量: {{ results.length }}</el-tag>
        </div>
        
        <div
          v-for="(result, index) in results"
          :key="index"
          class="description-item"
        >
          <div class="description-header">
            <h4>描述 {{ index + 1 }}</h4>
            <div class="description-actions">
              <el-button
                type="text"
                size="small"
                @click="copyDescription(result.description)"
                :icon="DocumentCopy"
              >
                复制
              </el-button>
              <el-button
                type="text"
                size="small"
                @click="useAsPrompt(result.description)"
                :icon="Refresh"
              >
                作为新输入
              </el-button>
            </div>
          </div>
          <div class="description-content">
            <pre>{{ result.description }}</pre>
          </div>
        </div>
        
        <div class="usage-tip">
          <el-alert
            title="使用提示"
            type="info"
            :closable="false"
            show-icon
          >
            <template #default>
              <p>生成的详细描述可以用于：</p>
              <ul>
                <li>🎨 AI图像生成工具（如Midjourney、DALL-E、Stable Diffusion）</li>
                <li>📝 创意写作和故事创作</li>
                <li>🎯 广告文案和营销素材</li>
                <li>🎬 影视剧本和分镜头描述</li>
              </ul>
            </template>
          </el-alert>
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
    
    <!-- 示例卡片 -->
    <el-card class="examples-card">
      <template #header>
        <span>💡 输入示例</span>
      </template>
      
      <div class="examples-container">
        <div class="example-category">
          <h4>人物场景</h4>
          <div class="example-tags">
            <el-tag
              v-for="example in personExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
              {{ example }}
            </el-tag>
          </div>
        </div>
        
        <div class="example-category">
          <h4>自然风景</h4>
          <div class="example-tags">
            <el-tag
              v-for="example in natureExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
              {{ example }}
            </el-tag>
          </div>
        </div>
        
        <div class="example-category">
          <h4>物品静物</h4>
          <div class="example-tags">
            <el-tag
              v-for="example in objectExamples"
              :key="example"
              class="example-tag"
              @click="useExample(example)"
            >
              {{ example }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { DocumentCopy, Refresh } from '@element-plus/icons-vue'

export default {
  name: 'ImageDescription',
  components: {
    DocumentCopy,
    Refresh
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
        ElMessage.warning('请输入基础描述')
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
        
        const response = await axios.post('/api/v1/ai/image/describe', requestData)
        
        if (response.data.success) {
          this.results = response.data.descriptions
          this.currentModel = response.data.model
          ElMessage.success('图像描述生成完成')
        } else {
          this.error = response.data.error || '生成失败'
          ElMessage.error('生成失败')
        }
      } catch (error) {
        console.error('生成请求失败:', error)
        this.error = error.response?.data?.detail || '网络请求失败'
        ElMessage.error('生成请求失败')
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
        ElMessage.success('描述已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        ElMessage.error('复制失败')
      }
    },
    
    async copyAllResults() {
      if (this.results.length === 0) return
      
      const allDescriptions = this.results
        .map((result, index) => `描述 ${index + 1}:\n${result.description}`)
        .join('\n\n---\n\n')
      
      try {
        await navigator.clipboard.writeText(allDescriptions)
        ElMessage.success('所有描述已复制到剪贴板')
      } catch (error) {
        console.error('复制失败:', error)
        ElMessage.error('复制失败')
      }
    },
    
    useAsPrompt(description) {
      this.form.prompt = description
      ElMessage.success('已将描述设为新的输入')
    },
    
    useExample(example) {
      this.form.prompt = example
      ElMessage.success('已使用示例作为输入')
    },
    
    getStyleLabel(style) {
      const labels = {
        'realistic': '写实风格',
        'artistic': '艺术风格',
        'cartoon': '卡通风格'
      }
      return labels[style] || style
    }
  }
}
</script>

<style scoped>
.image-description {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 12px;
  color: #909399;
  font-size: 12px;
}

.result-card {
  margin-top: 20px;
}

.error-card {
  margin-top: 20px;
}

.examples-card {
  margin-top: 20px;
}

.results-container {
  padding: 10px 0;
}

.result-meta {
  margin-bottom: 20px;
}

.result-meta .el-tag {
  margin-right: 8px;
  margin-bottom: 8px;
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

.error-card p {
  color: #f56c6c;
  margin: 0;
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
  background-color: #409EFF;
  color: white;
  transform: translateY(-2px);
}
</style>