<template>
  <div class="home">
    <a-row :gutter="20">
      <a-col :span="24">
        <div class="welcome-section">
          <h1>欢迎使用AI服务平台</h1>
          <p>基于大模型API的纯AI服务，提供文本分析、代码助手、智能对话等功能</p>
        </div>
      </a-col>
    </a-row>

    <a-row :gutter="20" class="feature-cards">
      <a-col :span="8">
        <a-card class="feature-card" @click="$router.push('/text')" hoverable>
          <div class="card-content">
            <FileTextOutlined class="feature-icon" style="color: #1677ff;" />
            <h3>文本分析</h3>
            <p>支持文本摘要、情感分析、关键词提取、翻译等多种分析任务</p>
          </div>
        </a-card>
      </a-col>

      <a-col :span="8">
        <a-card class="feature-card" @click="$router.push('/code')" hoverable>
          <div class="card-content">
            <CodeOutlined class="feature-icon" style="color: #52c41a;" />
            <h3>代码助手</h3>
            <p>代码审查、优化建议、错误调试、代码生成和解释</p>
          </div>
        </a-card>
      </a-col>

      <a-col :span="8">
        <a-card class="feature-card" @click="$router.push('/chat')" hoverable>
          <div class="card-content">
            <MessageOutlined class="feature-icon" style="color: #faad14;" />
            <h3>智能对话</h3>
            <p>多轮对话交互，支持自定义系统提示词和多种AI模型</p>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="20" class="feature-cards">
      <a-col :span="8">
        <a-card class="feature-card" @click="$router.push('/ocr')" hoverable>
          <div class="card-content">
            <CameraOutlined class="feature-icon" style="color: #f5222d;" />
            <h3>文字识别</h3>
            <p>通过视觉模型识别图片中的文字，支持多语言和不同精度</p>
          </div>
        </a-card>
      </a-col>

      <a-col :span="8">
        <a-card class="feature-card" @click="$router.push('/image')" hoverable>
          <div class="card-content">
            <PictureOutlined class="feature-icon" style="color: #909399;" />
            <h3>图像描述</h3>
            <p>生成详细的图像描述，可用于图像生成和内容创作</p>
          </div>
        </a-card>
      </a-col>

      <a-col :span="24" :md="8">
        <a-card class="stats-card">
          <div class="card-content">
            <BarChartOutlined class="feature-icon" style="color: #1677ff;" />
            <h3>服务统计</h3>
            <div class="stats">
              <p>可用模型: <strong>{{ modelCount }}</strong></p>
              <p>服务状态: <strong :class="{'online': isOnline, 'offline': !isOnline}">{{ isOnline ? '在线' : '离线' }}</strong></p>
            </div>
          </div>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="20" class="info-section">
      <a-col :span="24" :md="12">
        <a-card>
          <template #title>
            <span>🌟 特性介绍</span>
          </template>
          <ul>
            <li><strong>纯AI驱动</strong>: 所有功能通过大模型API实现</li>
            <li><strong>多模型支持</strong>: 支持GLM、Kimi等多种AI模型</li>
            <li><strong>极简架构</strong>: 无需复杂的第三方处理库</li>
            <li><strong>RESTful API</strong>: 标准化接口设计</li>
            <li><strong>免费使用</strong>: 基于免费的AI模型服务</li>
          </ul>
        </a-card>
      </a-col>

      <a-col :span="24" :md="12">
        <a-card>
          <template #title>
            <span>📚 使用说明</span>
          </template>
          <ol>
            <li>选择对应的功能模块</li>
            <li>输入要处理的内容</li>
            <li>选择合适的AI模型（可选）</li>
            <li>点击处理获取AI分析结果</li>
            <li>查看和复制处理结果</li>
          </ol>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import axios from 'axios'
import {
  FileTextOutlined,
  CodeOutlined,
  MessageOutlined,
  CameraOutlined,
  PictureOutlined,
  BarChartOutlined
} from '@ant-design/icons-vue'

export default {
  name: 'Home',
  components: {
    FileTextOutlined,
    CodeOutlined,
    MessageOutlined,
    CameraOutlined,
    PictureOutlined,
    BarChartOutlined
  },
  data() {
    return {
      modelCount: 0,
      isOnline: false
    }
  },
  async mounted() {
    await this.checkServiceStatus()
  },
  methods: {
    async checkServiceStatus() {
      try {
        const response = await axios.get('/api/v1/ai/health')
        this.isOnline = response.data.status === 'healthy'
        
        const modelsResponse = await axios.get('/api/v1/ai/models')
        this.modelCount = modelsResponse.data.models.length
      } catch (error) {
        console.error('检查服务状态失败:', error)
        this.isOnline = false
      }
    }
  }
}
</script>

<style scoped>
.home {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding: 48px 32px;
  background: linear-gradient(135deg, #f4f9ff 0%, #e8f1ff 45%, #fef6ff 100%);
  color: #1f2937;
  border-radius: 18px;
  box-shadow:
    0 20px 40px rgba(79, 114, 255, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
}

.welcome-section::before,
.welcome-section::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  opacity: 0.35;
  pointer-events: none;
}

.welcome-section::before {
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, rgba(79, 114, 255, 0.35) 0%, rgba(79, 114, 255, 0) 60%);
  top: -120px;
  right: -60px;
}

.welcome-section::after {
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(255, 166, 204, 0.35) 0%, rgba(255, 166, 204, 0) 60%);
  bottom: -120px;
  left: -80px;
}

.welcome-section h1 {
  font-size: 2.6em;
  margin-bottom: 18px;
  font-weight: 600;
  color: #1d1f2f;
}

.welcome-section p {
  font-size: 1.16em;
  color: #4b5563;
  max-width: 700px;
  margin: 0 auto;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 200px;
}

.stats-card {
  height: 200px;
}

.card-content {
  text-align: center;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-content h3 {
  margin: 16px 0 12px 0;
  color: #333;
}

.card-content p {
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.stats {
  margin-top: 20px;
}

.stats p {
  margin: 8px 0;
  font-size: 14px;
}

.online {
  color: #67C23A;
}

.offline {
  color: #F56C6C;
}

.feature-icon {
  font-size: 48px;
}

.info-section {
  margin-top: 40px;
}

.info-section ul, .info-section ol {
  padding-left: 20px;
}

.info-section li {
  margin: 8px 0;
  line-height: 1.6;
}
</style>