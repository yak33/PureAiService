# AI 服务平台 (Pure AI Service)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Vue 3](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)

一个完全基于大模型API实现的AI服务，不依赖任何文档处理库（如PyPDF2、python-docx等），所有功能都通过调用大模型API来实现。

## 📖 文档

- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)
- [更新日志](CHANGELOG.md)
- [许可证](LICENSE)

## 🌟 特性

- **纯AI驱动**: 所有功能通过大模型API实现，无需第三方处理库。实时显示硅基流动平台账户余额和状态。
- **动态模型管理**: 从硅基流动平台获取模型列表，用户自主选择配置可用模型 🆕
- **功能丰富**: 文本分析、代码辅助、智能对话、OCR识别、图像描述、**AI图片编辑**等
- **用户认证系统**: 完整的JWT认证、用户注册登录、滑动验证码保护
- **现代化前端**: 基于 Vue 3 + Ant Design Vue 的美观Web界面
- **请求日志**: 完整记录所有API请求和响应，便于调试 🆕
- **高度可扩展**: 轻松添加新的 AI 功能
- **极简架构**: 只保留必要的文件和依赖
- **高可靠调用**: 后端使用异步 `httpx` 调用硅基流动 API，支持流式响应并强化错误处理

## 🆕 最新功能 (2025-10-02)

### 🎯 动态模型配置
- **模型列表获取及自主配置**: 从硅基流动平台实时获取所有可用模型，可自行选择并启用需要的模型，支持按类型、子类型筛选，支持模型名称模糊搜索。 一键过滤 Pro/ 开头的付费模型。模型配置保存到 data/models_config.json
### 💰 账户信息集成
- **实时余额账户状态监控**: 导航栏显示硅基流动平台账户余额，显示账户状态（正常/异常），路由切换时自动更新账户信息

### 📊 请求响应日志
- **完整记录**: 记录所有API请求参数和响应内容，显示每个请求的处理时间，格式化输出

### 🎨 UI/UX优化
- **首页模型滚动展示**: 动态滚动显示所有配置的模型，替代单一数字

### ⚙️ 配置优化
- **移除默认模型**: 要求用户必须先配置模型才能使用
- **移除硬编码配置**: 删除 siliconflow_models.py，改为动态配置
- **环境变量更新**: 更新 .env.example，注释掉已弃用的配置

## 🗂️ 项目结构

```
ai-service/
│
├── app/                        # 应用主目录
│   ├── api/                   # API接口
│   │   ├── ai_endpoints.py   # AI服务端点
│   │   ├── auth_endpoints.py # 认证端点
│   │   └── __init__.py
│   │
│   ├── core/                  # 核心配置
│   │   ├── config.py         # 应用配置
│   │   ├── logger.py         # 日志配置
│   │   ├── auth.py           # JWT认证逻辑
│   │   ├── user_manager.py   # 用户管理
│   │   ├── models_config_manager.py  # 模型配置管理器
│   │   ├── request_logging_middleware.py  # 请求日志中间件
│   │   └── __init__.py
│   │
│   ├── services/              # 服务层
│   │   ├── pure_ai_service.py # 纯AI服务实现
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── frontend/                  # 前端项目（Vue 3 + Ant Design Vue）
│   ├── src/                  # 源代码
│   │   ├── views/           # 页面组件
│   │   │   ├── Home.vue            # 首页
│   │   │   ├── Login.vue           # 登录页面
│   │   │   ├── TextAnalysis.vue    # 文本分析
│   │   │   ├── CodeAssist.vue      # 代码助手
│   │   │   ├── Chat.vue            # 智能对话
│   │   │   ├── OCR.vue             # 文字识别
│   │   │   ├── ImageDescription.vue # 图像描述
│   │   │   ├── ImageEdit.vue       # 图片编辑
│   │   │   └── ModelsManagement.vue # 模型管理 🆕
│   │   ├── components/      # 组件
│   │   │   └── SliderCaptcha.vue   # 滑动验证码 🆕
│   │   ├── services/        # API服务
│   │   │   └── api.js              # API封装
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口文件
│   ├── package.json         # 前端依赖
│   ├── vite.config.js       # 构建配置
│   └── README.md            # 前端说明
│
├── data/                      # 数据目录
│   ├── users.json            # 用户数据
│   └── models_config.json    # 模型配置 🆕
├── logs/                      # 日志目录
├── .env                       # 环境变量配置
├── .env.example              # 环境变量示例
├── .gitignore                # Git忽略文件
├── main.py                   # 主程序入口
├── start.py                  # 快速启动脚本
├── requirements.txt          # Python依赖
├── test_ai_service.py        # 测试脚本
└── README.md                 # 项目说明文档
```

### 📄 核心文件说明

**后端文件：**
- **main.py**: FastAPI应用主入口，配置中间件和路由
- **start.py**: 便捷启动脚本，一键运行服务
- **.env**: 配置API密钥和服务参数
- **app/services/pure_ai_service.py**: 核心AI服务类，所有功能通过大模型API实现
- **app/core/models_config_manager.py**: 动态模型配置管理器
- **data/models_config.json**: 用户配置的可用模型列表

**前端文件：**
- **frontend/**: Vue 3前端项目目录
- **frontend/dist/**: 前端构建后的静态文件（部署到Nginx）

## 📦 安装

### 1. 克隆项目
```bash
git clone https://github.com/yak33/ai-service.git
cd ai-service
```

### 2. 安装后端依赖

```bash
# 使用pip直接安装
pip install -r requirements.txt

# 或使用conda环境
conda create -n ai-service python=3.11
conda activate ai-service
pip install -r requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend

# 使用pnpm（推荐）
npm install -g pnpm
pnpm install

# 或使用npm
npm install
```

### 4. 配置环境

复制 `.env.example` 为 `.env`，然后配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件：
```env
# 应用基本配置
APP_NAME='Pure AI Service'
DEBUG=false
HOST=0.0.0.0
PORT=8000

# AI服务配置 - 硅基流动平台
OPENAI_API_KEY=your_siliconflow_api_key_here

# 默认参数配置（模型需在模型管理页面配置）
# DEFAULT_MODEL=  # 已弃用，请在模型管理页面选择模型
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2000

# 认证配置
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=123456
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

**重要提醒**: 
- 请将 `your_siliconflow_api_key_here` 替换为你的真实API密钥
- 请修改 `JWT_SECRET_KEY` 为随机字符串
- 请修改默认管理员密码
- **首次使用前，请访问"模型管理"页面配置可用模型**
- 确保 `.env` 文件已添加到 `.gitignore` 中，避免密钥泄露

## 🚀 启动服务

### 🎯 开发模式（推荐）

适用于本地开发，支持热重载：

```bash
# 终端1：启动后端服务
python main.py
# 或
python start.py

# 终端2：启动前端开发服务器
cd frontend
pnpm dev  # 或 npm run dev
```

前端会自动在浏览器打开 http://localhost:3000

### 🔧 仅启动后端API服务

```bash
# 方式1：使用快速启动脚本
python start.py

# 方式2：使用main.py
python main.py

# 方式3：使用uvicorn命令
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 📱 访问地址

**开发模式（推荐用于本地开发）:**
- 🎨 **前端界面**: http://localhost:3000 （Vue开发服务器，热重载）
- 🔌 **后端API**: http://localhost:8000 （FastAPI服务）
- 📚 **API文档**: http://localhost:8000/docs （可交互测试）
- 📊 **ReDoc文档**: http://localhost:8000/redoc （只读文档）

> 💡 **说明**: 前端运行在3000端口，通过Vite代理自动调用后端8000端口的API接口

**生产部署（Linux服务器）:**
- 🎨 **前端界面**: 通过Nginx服务（如 http://your-domain.com 或 http://your-ip:80）
- 🔌 **后端API**: 8000端口（通过Nginx反向代理到 `/api` 路径）
- 📚 **API文档**: http://your-domain.com/docs

> 💡 **部署说明**: 前端静态文件由Nginx直接服务，API请求通过Nginx代理到后端8000端口

**默认账号:**
- 👤 用户名: `admin`
- 🔑 密码: `123456` （首次启动自动创建）

## 🎯 快速开始

### 1. 登录系统
- **开发模式**: 访问 http://localhost:3000 （前端自动代理后端8000端口）
- **生产环境**: 访问你的域名或服务器IP（由Nginx配置）

使用默认账号登录

### 2. 配置模型（必须）
1. 点击导航栏的"模型管理"菜单
2. 点击"刷新列表"按钮，从硅基流动平台获取可用模型
3. 使用筛选和搜索功能找到需要的模型
4. 勾选需要使用的模型（建议勾选"仅显示免费模型"）
5. 点击"保存配置"按钮

### 3. 开始使用
配置完模型后，即可使用各项AI功能：
- 文本分析、代码助手、智能对话等

## 📊 支持的模型

### 动态模型配置 🆕
本系统支持从硅基流动平台动态获取所有可用模型，用户可以自主选择并配置需要使用的模型。

### 推荐的免费模型
以下是一些常用的免费模型，您可以在模型管理页面搜索并启用：

**文本对话模型：**
- `zai-org/GLM-4.5` - 智谱AI对话模型（推荐）
- `moonshotai/Kimi-K2-Instruct-0905` - Moonshot AI对话模型

**视觉模型：**
- `zai-org/GLM-4.5V` - 智谱AI视觉语言模型（OCR识别）
- `OpenGVLab/InternVL2-26B` - 视觉理解模型

**图片编辑模型：**
- `Qwen/Qwen-Image-Edit-2509` - 通义千问图片编辑模型
  - 支持背景更换、物体添加/移除
  - 支持颜色调整、风格转换
  - 基于自然语言指令的智能编辑

**注意：** 模型可用性和免费额度可能随时变化，请以硅基流动平台实际为准。建议在模型管理页面勾选"仅显示免费模型"来过滤付费模型。

## 📝 注意事项

1. **API密钥**: 确保配置了正确的硅基流动平台API密钥
2. **速率限制**: 免费模型有调用频率限制（通常10-20次/分钟）
3. **Token限制**: 不同模型有不同的最大Token限制
4. **费用**: 部分模型是收费的，请查看模型列表了解价格
5. **图片编辑**: 编辑后的图片URL有效期为1小时，建议及时下载保存

## 📦 技术栈

### 后端依赖
- **fastapi**: Web框架
- **uvicorn[standard]**: ASGI服务器
- **httpx**: 异步HTTP客户端
- **pydantic**: 数据验证
- **python-dotenv**: 环境变量
- **loguru**: 日志管理
- **aiofiles**: 异步文件处理
- **python-multipart**: 文件上传支持
- **PyJWT**: JWT Token认证 🆕
- **passlib**: 密码加密 🆕
- **python-jose**: JWT编码解码 🆕

### 前端依赖
- **Vue 3**: 渐进式JavaScript框架
- **Ant Design Vue**: Vue 3 组件库
- **Vue Router**: 官方路由管理器
- **Axios**: HTTP客户端
- **Vite**: 现代化构建工具
- **npm/pnpm**: 包管理器

## 💡 设计理念

本项目采用"AI-First"设计理念：
- **所有文档处理通过AI理解**而非解析库（无需PyPDF2、python-docx等）
- **OCR通过视觉语言模型**而非tesseract
- **代码分析通过代码模型**而非AST解析
- **图片编辑通过AI模型**而非传统图像处理库（支持自然语言指令）
- **充分利用大模型**的理解和生成能力

## 🔧 故障排除

### 后端服务问题
- **服务无法启动**: 检查Python版本（需要3.8+）、确认依赖已正确安装、查看日志文件 `logs/app.log`
- **API调用失败**: 检查API密钥是否正确、确认网络可以访问 `api.siliconflow.cn`、查看具体错误信息
- **模型不可用**: 某些模型可能需要特殊权限、使用免费模型进行测试、查看模型列表确认可用模型

### 前端服务问题
- **依赖安装失败**: 尝试使用不同的镜像源、清理缓存后重新安装、使用pnpm替代npm
- **页面无法访问**: 检查端口是否被占用、确认后端服务已启动、检查代理配置
- **API请求失败**: 确认后端服务运行正常、检查网络连接、查看浏览器控制台错误信息

## 🤝 贡献

我们欢迎并感谢所有形式的贡献！

### 如何贡献

1. 🐛 **报告Bug** - 在 [Issues](https://github.com/yak33/PureAiService/issues) 中提交问题
2. 💡 **提出建议** - 分享你的想法和改进建议
3. 📝 **改进文档** - 帮助完善文档和示例
4. 🔧 **提交代码** - Fork 项目并提交 Pull Request

详细的贡献指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 👨‍💻 作者

**ZHANGCHAO**

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

这意味着你可以自由地：
- ✅ 商业使用
- ✅ 修改代码
- ✅ 分发
- ✅ 私人使用

但需要：
- ⚠️ 包含许可证和版权声明

## ⭐ Star History

如果这个项目对你有帮助，请给它一个 Star ⭐️

## 📞 联系方式

- 📧 提交 [Issue](https://github.com/yak33/PureAiService/issues)
- 💬 参与 [讨论](https://github.com/yak33/PureAiService/discussions)

---

**Made with ❤️ by ZHANGCHAO**
