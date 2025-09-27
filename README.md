# 纯AI服务 (Pure AI Service)

一个完全基于大模型API实现的AI服务，不依赖任何文档处理库（如PyPDF2、python-docx等），所有功能都通过调用大模型API来实现。

## 🌟 特性

- **纯AI驱动**: 所有功能通过大模型API实现，无需第三方处理库
- **多模型支持**: 支持硅基流动平台的AI模型（GLM和Kimi）
- **功能丰富**: 文本分析、代码辅助、OCR识别、图像描述生成等
- **现代化前端**: 基于Vue 3 + Element Plus的美观Web界面
- **简单易用**: RESTful API设计，易于集成
- **高度可扩展**: 轻松添加新的AI功能
- **极简架构**: 只保留必要的文件和依赖
- **高可靠调用**: 后端使用异步 `httpx` 调用硅基流动 API，支持流式响应并强化错误处理

## 🆕 最近更新

- **后端异步改造**：`app/services/pure_ai_service.py` 迁移至 `httpx.AsyncClient`，默认复用 `.env` 配置的超时与模型，增强流式解析与错误信息输出。
- **安全日志**：新增鉴权头脱敏与错误详情提取逻辑，更便于排查问题同时避免泄露密钥。
- **测试脚本升级**：`test_ai_service.py` 改写为异步版，统一通过 `httpx.AsyncClient` 调用后端接口，运行方式依旧为 `python test_ai_service.py`。

## 🗂️ 项目结构

```
ai-service/
│
├── app/                        # 应用主目录
│   ├── api/                   # API接口
│   │   ├── ai_endpoints.py   # AI服务端点（所有API路由）
│   │   └── __init__.py
│   │
│   ├── core/                  # 核心配置
│   │   ├── config.py         # 应用配置
│   │   ├── logger.py         # 日志配置
│   │   ├── siliconflow_models.py  # 模型配置
│   │   └── __init__.py
│   │
│   ├── services/              # 服务层
│   │   ├── pure_ai_service.py # 纯AI服务实现
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── frontend/                  # 前端项目
│   ├── src/                  # 源代码
│   │   ├── views/           # 页面组件
│   │   ├── services/        # API服务
│   │   ├── App.vue          # 根组件
│   │   └── main.js          # 入口文件
│   ├── package.json         # 前端依赖
│   ├── vite.config.js       # 构建配置
│   └── README.md            # 前端说明
│
├── static/                    # 前端构建输出（自动生成）
├── logs/                      # 日志目录
├── .env                       # 环境变量配置
├── .gitignore                # Git忽略文件
├── main.py                   # 主程序入口
├── start.py                  # 快速启动脚本
├── requirements.txt          # Python依赖
├── test_ai_service.py        # 测试脚本
└── README.md                 # 项目说明文档
```

### 📄 核心文件说明

**后端文件：**
- **main.py**: FastAPI应用主入口，配置中间件和路由，集成前端静态文件服务
- **start.py**: 便捷启动脚本，一键运行服务
- **.env**: 配置API密钥和服务参数
- **pure_ai_service.py**: 核心AI服务类，所有功能通过大模型API实现
- **siliconflow_models.py**: 硅基流动平台模型配置（GLM和Kimi）

**前端文件：**
- **frontend/**: Vue 3前端项目目录
- **static/**: 前端构建后的静态文件（由后端服务托管）

## 📦 安装

### 1. 克隆项目
```bash
git clone https://github.com/yourusername/ai-service.git
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

编辑 `.env` 文件，配置API密钥：
```env
# AI服务配置 - 硅基流动平台
OPENAI_API_KEY=your_siliconflow_api_key_here
OPENAI_BASE_URL=https://api.siliconflow.cn/v1

# 默认模型配置
DEFAULT_MODEL=zai-org/GLM-4.5
```

**重要提醒**: 
- 请将 `your_siliconflow_api_key_here` 替换为你的真实API密钥
- 确保 `.env` 文件已添加到 `.gitignore` 中，避免密钥泄露

## 🚀 启动服务

### 🎯 完整服务启动（前端+后端）

#### 方式1：一键启动（推荐）
```bash
# 1. 构建前端
cd frontend
pnpm build  # 或 npm run build

# 2. 启动后端服务（包含前端界面）
cd ..
python start.py
```

#### 方式2：分别启动（开发模式）
```bash
# 终端1：启动后端服务
python main.py

# 终端2：启动前端开发服务器
cd frontend
pnpm dev  # 或 npm run dev
```

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

**完整服务（推荐）:**
- 🎨 **Web界面**: http://localhost:8000 （现代化前端界面）
- 📚 **API文档**: http://localhost:8000/docs （可交互测试）
- 📊 **ReDoc文档**: http://localhost:8000/redoc （只读文档）

**开发模式:**
- 🎨 **前端开发**: http://localhost:3000 （热重载，自动打开浏览器）
- 🔌 **后端API**: http://localhost:8000

## 📚 API接口

### 1. 文本分析
```python
POST /api/v1/ai/text/analyze
{
    "text": "要分析的文本",
    "task": "analyze",  # 可选: analyze, summarize, extract, translate, sentiment, classify, keywords
    "custom_prompt": "自定义提示词（可选）",
    "model": "模型ID（可选）"
}
```

### 2. 代码辅助
```python
POST /api/v1/ai/code
{
    "code": "源代码（可选）",
    "task": "review",  # 可选: review, optimize, explain, debug, generate, convert, test, document
    "language": "Python",
    "requirements": "具体要求"
}
```

### 3. 对话接口
```python
POST /api/v1/ai/chat
{
    "messages": [
        {"role": "user", "content": "你好"}
    ],
    "system_prompt": "系统提示词（可选）",
    "model": "模型ID（可选）",
    "temperature": 0.7,
    "max_tokens": 2000
}
```

### 4. OCR识别（通过视觉模型）
```python
POST /api/v1/ai/ocr
FormData:
- file: 图片文件
- language: auto/zh/en/mix
- detail_level: high/medium/low
```

### 5. 图像描述生成
```python
POST /api/v1/ai/image/describe
{
    "prompt": "简单描述",
    "model": "zai-org/GLM-4.5",
    "style": "realistic",  # 可选: realistic, artistic, cartoon
    "n": 1
}
```

### 6. 快速AI调用
```python
POST /api/v1/ai/quick
{
    "prompt": "直接输入提示词",
    "model": "模型ID（可选）"
}
```

### 7. 批量处理
```python
POST /api/v1/ai/batch
{
    "tasks": [
        {
            "id": "task1",
            "type": "text",
            "text": "文本内容",
            "task": "analyze"
        },
        {
            "id": "task2",
            "type": "code",
            "code": "代码内容",
            "task": "review"
        }
    ]
}
```

### 8. 获取模型列表
```python
GET /api/v1/ai/models
```

## 🧪 测试

运行测试脚本：
```bash
# 确保服务已启动，然后运行
python test_ai_service.py
```

## 📊 支持的模型

### 文本模型
- **GLM-4.5**: 智谱AI对话模型（默认，免费）
- **Kimi-K2**: Moonshot AI文本对话模型（免费）

### 视觉模型（用于OCR）
- **GLM-4.5V**: 智谱AI视觉语言模型（免费）

## 💡 使用示例

### Python示例
```python
import requests

# 文本分析
response = requests.post(
    "http://localhost:8000/api/v1/ai/text/analyze",
    json={
        "text": "人工智能正在改变世界",
        "task": "sentiment"
    }
)
print(response.json())

# 代码生成
response = requests.post(
    "http://localhost:8000/api/v1/ai/code",
    json={
        "task": "generate",
        "language": "Python",
        "requirements": "写一个快速排序算法"
    }
)
print(response.json())
```

### cURL示例
```bash
# 快速AI调用
curl -X POST http://localhost:8000/api/v1/ai/quick \
  -H "Content-Type: application/json" \
  -d '{"prompt": "解释什么是区块链"}'

# 获取模型列表
curl http://localhost:8000/api/v1/ai/models
```

## 📝 注意事项

1. **API密钥**: 确保配置了正确的硅基流动平台API密钥
2. **速率限制**: 免费模型有调用频率限制（通常10-20次/分钟）
3. **Token限制**: 不同模型有不同的最大Token限制
4. **费用**: 部分模型是收费的，请查看模型列表了解价格

## 📦 技术栈

### 后端依赖
- **fastapi**: Web框架
- **uvicorn[standard]**: ASGI服务器
- **requests**: HTTP客户端
- **pydantic**: 数据验证
- **python-dotenv**: 环境变量
- **loguru**: 日志管理
- **aiofiles**: 异步文件处理
- **python-multipart**: 文件上传支持

### 前端依赖
- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: Vue 3组件库
- **Vue Router**: 官方路由管理器
- **Axios**: HTTP客户端
- **Vite**: 现代化构建工具
- **pnpm**: 快速、节省磁盘空间的包管理器

## 💡 设计理念

本项目采用"AI-First"设计理念：
- **所有文档处理通过AI理解**而非解析库（无需PyPDF2、python-docx等）
- **OCR通过视觉语言模型**而非tesseract
- **代码分析通过代码模型**而非AST解析
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

### 常见解决方案
```bash
# 清理并重新安装依赖
cd frontend
rm -rf node_modules package-lock.json
pnpm install

# 重新构建前端
pnpm build

# 重启完整服务
cd ..
python start.py
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请提交Issue或联系维护者。