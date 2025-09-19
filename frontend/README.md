# AI服务前端界面

基于 Vue 3 + Element Plus 的现代化AI服务前端界面。

## 🌟 特性

- **现代化UI**: 基于Element Plus的美观界面设计
- **响应式布局**: 适配各种屏幕尺寸
- **实时交互**: 支持文件上传、实时对话等交互功能
- **多功能集成**: 文本分析、代码助手、OCR识别等完整功能
- **用户友好**: 直观的操作流程和丰富的使用提示

## 🛠️ 技术栈

- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: Vue 3组件库
- **Vue Router**: 官方路由管理器
- **Axios**: HTTP客户端
- **Vite**: 现代化构建工具
- **pnpm**: 快速、节省磁盘空间的包管理器

## 📦 安装依赖

### 使用 pnpm (推荐)

```bash
cd frontend

# 安装 pnpm (如果还没有安装)
npm install -g pnpm

# 安装项目依赖
pnpm install
```

### 使用 npm (备选)

```bash
cd frontend
npm install
```

## 🚀 开发运行

### 使用 pnpm
```bash
pnpm dev
```

### 使用 npm
```bash
npm run dev
```

访问 http://localhost:3000

## 🏗️ 构建部署

### 使用 pnpm
```bash
pnpm build
```

### 使用 npm
```bash
npm run build
```

构建文件将输出到 `../static` 目录，可直接被后端服务托管。

## 📋 pnpm 相关命令

```bash
# 安装依赖
pnpm install

# 添加新依赖
pnpm add <package-name>

# 添加开发依赖
pnpm add -D <package-name>

# 更新依赖
pnpm update

# 清理缓存
pnpm store prune

# 查看依赖树
pnpm list

# 运行脚本
pnpm dev
pnpm build
pnpm preview
```

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── views/             # 页面组件
│   │   ├── Home.vue       # 首页
│   │   ├── TextAnalysis.vue # 文本分析
│   │   ├── CodeAssist.vue   # 代码助手
│   │   ├── Chat.vue         # 智能对话
│   │   ├── OCR.vue          # 文字识别
│   │   └── ImageDescription.vue # 图像描述
│   ├── services/          # API服务
│   │   └── api.js         # API封装
│   ├── App.vue            # 根组件
│   └── main.js            # 入口文件
├── package.json
├── vite.config.js         # Vite配置
└── README.md
```

## 🎯 功能介绍

### 1. 首页 (Home)
- 服务概览和状态检查
- 功能导航卡片
- 使用说明和特性介绍

### 2. 文本分析 (TextAnalysis)
- 支持多种分析任务（摘要、翻译、情感分析等）
- 自定义提示词
- 结果复制和导出

### 3. 代码助手 (CodeAssist)
- 代码审查、优化、调试
- 多语言支持
- 代码生成和转换
- 结果下载

### 4. 智能对话 (Chat)
- 多轮对话交互
- 自定义系统提示词
- 对话历史保存
- 高级参数调整

### 5. 文字识别 (OCR)
- 图片文字识别
- 多语言和精度选择
- 拖拽上传支持
- 结果导出

### 6. 图像描述 (ImageDescription)
- 详细图像描述生成
- 多种风格选择
- 批量生成支持
- 使用示例提供

## 🔧 配置说明

### Vite配置 (vite.config.js)
- 开发服务器端口: 3000
- API代理: 自动转发到后端8000端口
- 构建输出: ../static目录

### API配置 (src/services/api.js)
- 基础URL: /api/v1
- 请求超时: 60秒
- 自动错误处理和日志记录

## 🎨 样式特色

- **渐变背景**: 首页使用渐变色背景
- **卡片悬停**: 功能卡片支持悬停动效
- **响应式设计**: 适配移动端和桌面端
- **统一配色**: 基于Element Plus主题色

## 📝 使用说明

1. **启动后端服务**: 确保AI服务后端正在运行
2. **安装依赖**: `npm install`
3. **启动开发**: `npm run dev`
4. **访问界面**: http://localhost:3000
5. **选择功能**: 点击首页功能卡片进入对应页面
6. **输入内容**: 根据页面提示输入相关内容
7. **获取结果**: 点击处理按钮获取AI分析结果

## 🔍 故障排除

### 常见问题

1. **API请求失败**
   - 检查后端服务是否启动
   - 确认端口配置正确

2. **页面加载慢**
   - 检查网络连接
   - 清除浏览器缓存

3. **文件上传失败**
   - 检查文件大小限制
   - 确认文件格式支持

## 🤝 开发建议

- **组件开发**: 遵循Vue 3 Composition API规范
- **样式编写**: 使用scoped样式避免污染
- **API调用**: 统一使用api.js中的封装方法
- **错误处理**: 合理使用Element Plus的消息提示

## 📄 许可证

MIT License