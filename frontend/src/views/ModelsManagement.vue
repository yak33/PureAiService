<template>
  <div class="models-management">
    <a-card title="📦 模型管理" class="management-card">
      <template #extra>
        <a-space>
          <a-button @click="loadPlatformModels" :loading="loading">
            <ReloadOutlined />
            刷新列表
          </a-button>
          <a-button type="primary" @click="saveConfig" :disabled="selectedModels.length === 0">
            <SaveOutlined />
            保存配置 ({{ selectedModels.length }})
          </a-button>
        </a-space>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <a-space size="middle" wrap style="width: 100%">
          <a-input-search v-model:value="searchText" placeholder="搜索模型名称（支持模糊匹配）" allow-clear style="width: 300px">
            <template #prefix>
              <SearchOutlined />
            </template>
          </a-input-search>

          <a-select v-model:value="filters.type" style="width: 120px" placeholder="全部类型" @change="loadPlatformModels">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="text">Text</a-select-option>
            <a-select-option value="image">Image</a-select-option>
            <a-select-option value="audio">Audio</a-select-option>
            <a-select-option value="video">Video</a-select-option>
          </a-select>

          <a-select v-model:value="filters.subType" style="width: 150px" placeholder="全部子类型"
            @change="loadPlatformModels">
            <a-select-option value="">全部</a-select-option>
            <a-select-option value="chat">Chat</a-select-option>
            <a-select-option value="embedding">Embedding</a-select-option>
            <a-select-option value="reranker">Reranker</a-select-option>
            <a-select-option value="text-to-image">Text-to-Image</a-select-option>
            <a-select-option value="image-to-image">Image-to-Image</a-select-option>
            <a-select-option value="speech-to-text">Speech-to-Text</a-select-option>
            <a-select-option value="text-to-video">Text-to-Video</a-select-option>
          </a-select>

          <a-checkbox v-model:checked="showOnlySelected">仅显示已选</a-checkbox>
          <a-checkbox v-model:checked="showOnlyFree">仅显示免费模型</a-checkbox>
        </a-space>
      </div>

      <!-- 统计信息 -->
      <a-alert v-if="configInfo" type="info" show-icon style="margin: 16px 0;">
        <template #message>
          当前已启用 <strong>{{ configInfo.total_models }}</strong> 个模型
          <span v-if="configInfo.updated_at">
            ，最后更新: {{ formatDate(configInfo.updated_at) }}
          </span>
        </template>
      </a-alert>

      <!-- 模型列表 -->
      <a-table :columns="columns" :data-source="filteredModels" :loading="loading"
        :pagination="{ pageSize: 20, showTotal: (total) => `共 ${total} 个模型` }" row-key="id" size="middle">
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'selection'">
            <a-checkbox :checked="isSelected(record.id)" @change="toggleSelection(record)" />
          </template>
          <template v-else-if="column.key === 'id'">
            <a-space>
              <a-tooltip :title="record.id">
                <span class="model-id">{{ record.id }}</span>
              </a-tooltip>
              <a-tag v-if="record.id.startsWith('Pro/')" color="orange" size="small">
                付费
              </a-tag>
            </a-space>
          </template>
          <template v-else-if="column.key === 'owned_by'">
            <a-tag color="blue">{{ record.owned_by || 'Unknown' }}</a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script>
import { aiService } from '../services/api'
import { message } from 'ant-design-vue'
import { ReloadOutlined, SaveOutlined, SearchOutlined } from '@ant-design/icons-vue'
import { clearModelsCache } from '../utils/modelCache'
import eventBus, { EVENT_MODELS_UPDATED } from '../utils/eventBus'

export default {
  name: 'ModelsManagement',
  components: {
    ReloadOutlined,
    SaveOutlined,
    SearchOutlined
  },
  data() {
    return {
      loading: false,
      platformModels: [],
      selectedModels: [],
      configInfo: null,
      filters: {
        type: '',
        subType: ''
      },
      searchText: '',
      showOnlySelected: false,
      showOnlyFree: false,
      columns: [
        {
          title: '选择',
          key: 'selection',
          width: 60,
          align: 'center'
        },
        {
          title: '模型ID',
          key: 'id',
          dataIndex: 'id',
          ellipsis: true
        },
        {
          title: '提供商',
          key: 'owned_by',
          dataIndex: 'owned_by',
          width: 150
        },
        {
          title: '创建时间',
          dataIndex: 'created',
          width: 120,
          customRender: ({ text }) => {
            return text ? new Date(text * 1000).toLocaleDateString() : '-'
          }
        }
      ]
    }
  },
  computed: {
    filteredModels() {
      let models = this.platformModels

      // 搜索过滤（模糊匹配）
      if (this.searchText && this.searchText.trim()) {
        const searchLower = this.searchText.toLowerCase().trim()
        models = models.filter(model =>
          model.id.toLowerCase().includes(searchLower)
        )
      }

      // 过滤付费模型
      if (this.showOnlyFree) {
        models = models.filter(model => !model.id.startsWith('Pro/'))
      }

      // 仅显示已选
      if (this.showOnlySelected) {
        models = models.filter(model => this.isSelected(model.id))
      }

      return models
    }
  },
  async mounted() {
    await this.loadConfig()
    await this.loadPlatformModels()
  },
  methods: {
    async loadConfig() {
      try {
        const response = await aiService.getModelsConfig()
        if (response.data.success) {
          this.selectedModels = response.data.enabled_models || []
          this.configInfo = response.data.config_info
        }
      } catch (error) {
        console.error('加载配置失败:', error)
      }
    },
    async loadPlatformModels() {
      this.loading = true
      try {
        const params = {}
        if (this.filters.type) params.type = this.filters.type
        if (this.filters.subType) params.sub_type = this.filters.subType

        const response = await aiService.getPlatformModels(params)
        if (response.data.success && response.data.data) {
          this.platformModels = response.data.data.data || []
          message.success(`加载了 ${this.platformModels.length} 个模型`)
        }
      } catch (error) {
        console.error('加载平台模型失败:', error)
        message.error('加载平台模型失败')
      } finally {
        this.loading = false
      }
    },
    isSelected(modelId) {
      return this.selectedModels.some(model => model.id === modelId)
    },
    toggleSelection(model) {
      const index = this.selectedModels.findIndex(m => m.id === model.id)
      if (index > -1) {
        this.selectedModels.splice(index, 1)
      } else {
        this.selectedModels.push(model)
      }
    },
    async saveConfig() {
      try {
        const response = await aiService.saveModelsConfig(this.selectedModels)
        if (response.data.success) {
          message.success(response.data.message)
          await this.loadConfig()

          // 清除模型缓存，让其他页面重新加载最新的模型列表
          clearModelsCache()
          console.log('模型配置已保存，缓存已清除')

          // 通知其他页面模型列表已更新
          eventBus.emit(EVENT_MODELS_UPDATED, {
            message: '模型配置已更新',
            timestamp: Date.now()
          })
          console.log('已发送模型更新事件通知')
        }
      } catch (error) {
        console.error('保存配置失败:', error)
        message.error(error.response?.data?.detail || '保存配置失败')
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.models-management {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.management-card {
  border-radius: 8px;
}

.filter-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
}

.model-id {
  font-family: 'Monaco', 'Consolas', monospace;
  font-size: 13px;
}
</style>
