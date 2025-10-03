# AI 服务平台前端界面

基于 Vue 3 + Ant Design Vue 的现代化AI服务前端界面。

## 🌟 特性

- **现代化UI**: 基于Ant Design Vue的美观界面设计
- **响应式布局**: 适配各种屏幕尺寸
- **用户认证**: 完整的登录系统和路由守卫
- **实时交互**: 支持文件上传、实时对话等交互功能
- **多功能集成**: 文本分析、代码助手、OCR识别、图像编辑等完整功能
- **用户友好**: 直观的操作流程和丰富的使用提示
- **滑块验证**: 安全的滑块验证码组件

## 🛠️ 技术栈

- **Vue 3**: 渐进式JavaScript框架
- **Ant Design Vue**: 企业级Vue 3组件库
- **Ant Design Icons**: 丰富的图标库
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

构建文件将输出到 `dist/` 目录。

### 预览构建结果
```bash
pnpm preview
```

这将启动一个本地静态服务器预览构建后的应用。

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
pnpm dev              # 启动开发服务器
pnpm build            # 构建生产版本
pnpm preview          # 预览构建结果
pnpm lint             # 代码检查和修复

# 项目维护
pnpm clean            # 清理pnpm缓存
pnpm clean:modules    # 删除node_modules
pnpm clean:lock       # 删除pnpm-lock.yaml
pnpm reset            # 完全重置项目依赖（删除node_modules和lock文件后重新安装）
```

## 📁 项目结构

```
frontend/
├── public/                      # 静态资源
├── src/
│   ├── views/                  # 页面组件
│   │   ├── Home.vue            # 首页
│   │   ├── Login.vue           # 登录页
│   │   ├── TextAnalysis.vue    # 文本分析
│   │   ├── CodeAssist.vue      # 代码助手
│   │   ├── Chat.vue            # 智能对话
│   │   ├── OCR.vue             # 文字识别
│   │   ├── ImageDescription.vue # 图像描述
│   │   ├── ImageEdit.vue       # 图像编辑
│   │   └── ModelsManagement.vue # 模型管理
│   ├── components/             # 通用组件
│   │   ├── Logo.vue            # Logo组件
│   │   └── SliderCaptcha.vue   # 滑块验证码
│   ├── services/               # API服务
│   │   └── api.js              # API封装
│   ├── utils/                  # 工具函数
│   ├── assets/                 # 静态资源
│   ├── App.vue                 # 根组件
│   └── main.js                 # 入口文件（含路由配置和守卫）
├── dist/                       # 构建输出目录
├── package.json                # 项目配置
├── pnpm-lock.yaml              # 依赖锁定文件
├── pnpm-workspace.yaml         # pnpm工作区配置
├── vite.config.js              # Vite配置
├── index.html                  # HTML入口
└── README.md                   # 项目文档
```

## 🎯 功能介绍

### 1. 登录页 (Login)
- 用户账号密码登录
- 滑块验证码验证
- Token认证管理
- 登录状态持久化

### 2. 首页 (Home)
- 服务概览和状态检查
- 功能导航卡片
- 使用说明和特性介绍
- 快速访问各功能模块

### 3. 文本分析 (TextAnalysis)
- 支持多种分析任务（摘要、翻译、情感分析等）
- 自定义提示词
- 结果复制和导出
- 历史记录查看

### 4. 代码助手 (CodeAssist)
- 代码审查、优化、调试
- 多语言支持
- 代码生成和转换
- 结果下载和复制

### 5. 智能对话 (Chat)
- 多轮对话交互
- 自定义系统提示词
- 对话历史保存
- 高级参数调整（温度、最大长度等）

### 6. 文字识别 (OCR)
- 图片文字识别
- 多语言和精度选择
- 拖拽上传支持
- 结果导出和复制

### 7. 图像描述 (ImageDescription)
- 详细图像描述生成
- 多种风格选择
- 批量生成支持
- 使用示例提供

### 8. 图像编辑 (ImageEdit)
- AI图像编辑功能
- 图像修复和增强
- 实时预览效果
- 多种编辑模式

### 9. 模型管理 (ModelsManagement)
- 查看和管理AI模型
- 模型配置和切换
- 模型状态监控
- 性能指标展示

## 🔧 配置说明

### Vite配置 (vite.config.js)
- **开发服务器端口**: 3000
- **自动打开浏览器**: 启动后自动打开
- **API代理**: 自动转发 `/api` 请求到后端 `http://localhost:8000`
- **构建输出**: `dist/` 目录
- **主机绑定**: `0.0.0.0`（支持局域网访问）

### API配置 (src/services/api.js)
- **基础URL**: `/api/v1`
- **请求超时**: 60秒
- **自动错误处理**: 统一的错误提示
- **Token管理**: 自动添加认证Token到请求头

### 路由配置 (src/main.js)
- **路由模式**: HTML5 History模式
- **路由守卫**: 自动检查登录状态
- **重定向**: 未登录自动跳转到登录页
- **公开路由**: 登录页无需认证

## 🎨 样式特色

- **企业级设计**: 基于Ant Design设计规范
- **渐变背景**: 首页使用渐变色背景
- **卡片悬停**: 功能卡片支持悬停动效
- **响应式设计**: 适配移动端和桌面端
- **统一配色**: 基于Ant Design主题色系
- **图标丰富**: 集成Ant Design Icons全套图标

## 📝 使用说明

1. **启动后端服务**: 确保AI服务后端正在运行（默认端口8000）
2. **安装依赖**: `pnpm install` 或 `npm install`
3. **启动开发**: `pnpm dev` 或 `npm run dev`
4. **访问界面**: http://localhost:3000 （会自动打开）
5. **登录系统**: 首次访问需要登录，输入账号密码并完成滑块验证
6. **选择功能**: 点击首页功能卡片进入对应页面
7. **输入内容**: 根据页面提示输入相关内容
8. **获取结果**: 点击处理按钮获取AI分析结果

## 🔍 故障排除

### 常见问题

1. **登录失败**
   - 检查账号密码是否正确
   - 确认后端认证服务正常运行
   - 检查滑块验证是否完成

2. **API请求失败**
   - 检查后端服务是否启动（端口8000）
   - 确认API代理配置正确
   - 检查Token是否有效（可能需要重新登录）

3. **页面加载慢**
   - 检查网络连接
   - 清除浏览器缓存
   - 使用 `pnpm reset` 重置项目依赖

4. **文件上传失败**
   - 检查文件大小限制
   - 确认文件格式支持
   - 查看浏览器控制台错误信息

5. **路由跳转异常**
   - 检查路由配置是否正确
   - 确认Token未过期
   - 清除localStorage重新登录

6. **依赖安装失败**
   - 尝试使用 `pnpm reset` 重置依赖
   - 检查网络连接和npm源配置
   - 使用 `pnpm store prune` 清理缓存

## 🤝 开发建议

- **组件开发**: 遵循Vue 3 Composition API规范
- **样式编写**: 使用scoped样式避免污染
- **UI组件**: 优先使用Ant Design Vue组件
- **API调用**: 统一使用 `api.js` 中的封装方法
- **错误处理**: 合理使用Ant Design的消息提示（message、notification）
- **代码规范**: 使用ESLint进行代码检查和格式化
- **图标使用**: 使用Ant Design Icons，在 `main.js` 中已全局注册
- **路由管理**: 新增页面需在 `main.js` 的 `routes` 数组中注册
- **状态管理**: Token等认证信息存储在localStorage中

## 📦 核心依赖版本

- **Vue**: ^3.4.0
- **Ant Design Vue**: ^4.2.6
- **Ant Design Icons Vue**: ^7.0.1
- **Vue Router**: ^4.2.5
- **Axios**: ^1.6.0
- **Vite**: ^5.0.0
- **pnpm**: >=8.0.0 (推荐使用10.17.0)

## 🔗 相关链接

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Ant Design Vue 文档](https://antdv.com/)
- [Ant Design Icons](https://ant-design.antgroup.com/components/icon-cn)
- [Vue Router 文档](https://router.vuejs.org/zh/)
- [Vite 文档](https://cn.vitejs.dev/)
- [pnpm 官网](https://pnpm.io/zh/)

## 👨‍💻 作者

ZHANGCHAO

## 📄 许可证

MIT License