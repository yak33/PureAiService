<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="welcome-section">
          <h1>欢迎使用AI服务平台</h1>
          <p>基于大模型API的纯AI服务，提供文本分析、代码助手、智能对话等功能</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/text')">
          <div class="card-content">
            <el-icon size="48" color="#409EFF"><Document /></el-icon>
            <h3>文本分析</h3>
            <p>支持文本摘要、情感分析、关键词提取、翻译等多种分析任务</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/code')">
          <div class="card-content">
            <el-icon size="48" color="#67C23A"><Cpu /></el-icon>
            <h3>代码助手</h3>
            <p>代码审查、优化建议、错误调试、代码生成和解释</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/chat')">
          <div class="card-content">
            <el-icon size="48" color="#E6A23C"><ChatDotRound /></el-icon>
            <h3>智能对话</h3>
            <p>多轮对话交互，支持自定义系统提示词和多种AI模型</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="feature-cards">
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/ocr')">
          <div class="card-content">
            <el-icon size="48" color="#F56C6C"><Camera /></el-icon>
            <h3>文字识别</h3>
            <p>通过视觉模型识别图片中的文字，支持多语言和不同精度</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="feature-card" @click="$router.push('/image')">
          <div class="card-content">
            <el-icon size="48" color="#909399"><Picture /></el-icon>
            <h3>图像描述</h3>
            <p>生成详细的图像描述，可用于图像生成和内容创作</p>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card class="stats-card">
          <div class="card-content">
            <el-icon size="48" color="#409EFF"><DataAnalysis /></el-icon>
            <h3>服务统计</h3>
            <div class="stats">
              <p>可用模型: <strong>{{ modelCount }}</strong></p>
              <p>服务状态: <strong :class="{'online': isOnline, 'offline': !isOnline}">{{ isOnline ? '在线' : '离线' }}</strong></p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="info-section">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>🌟 特性介绍</span>
          </template>
          <ul>
            <li><strong>纯AI驱动</strong>: 所有功能通过大模型API实现</li>
            <li><strong>多模型支持</strong>: 支持GLM、Kimi等多种AI模型</li>
            <li><strong>极简架构</strong>: 无需复杂的第三方处理库</li>
            <li><strong>RESTful API</strong>: 标准化接口设计</li>
            <li><strong>免费使用</strong>: 基于免费的AI模型服务</li>
          </ul>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>📚 使用说明</span>
          </template>
          <ol>
            <li>选择对应的功能模块</li>
            <li>输入要处理的内容</li>
            <li>选择合适的AI模型（可选）</li>
            <li>点击处理获取AI分析结果</li>
            <li>查看和复制处理结果</li>
          </ol>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
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
  padding: 40px 20px;
  background: linear-gradient(135deg, #0f0f0f 0%, #1e1e1e 50%, #0a0a0a 100%);
  color: #ffffff;
  border-radius: 12px;
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1),
    0 0 20px rgba(30, 30, 30, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.welcome-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 100%; }
}

.welcome-section h1 {
  font-size: 2.5em;
  margin-bottom: 16px;
  font-weight: 300;
}

.welcome-section p {
  font-size: 1.2em;
  opacity: 0.9;
}

.feature-cards {
  margin-bottom: 30px;
}

.feature-card {
  cursor: pointer;
  transition: all 0.3s ease;
  height: 200px;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
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