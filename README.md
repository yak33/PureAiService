# 纯AI服务 (Pure AI Service)

一个完全基于大模型API实现的AI服务，不依赖任何文档处理库（如PyPDF2、python-docx等），所有功能都通过调用大模型API来实现。

## 🌟 特性

- **纯AI驱动**: 所有功能通过大模型API实现，无需第三方处理库
- **多模型支持**: 支持硅基流动平台的多种AI模型（GLM、Kimi、Qwen等）
- **功能丰富**: 文本分析、代码辅助、智能对话、OCR识别、图像描述、**AI图片编辑**等
- **用户认证系统**: 完整的JWT认证、用户注册登录、滑动验证码保护
- **现代化前端**: 基于 Vue 3 + Ant Design Vue 的美观Web界面
- **简单易用**: RESTful API设计，易于集成
- **高度可扩展**: 轻松添加新的AI功能
- **极简架构**: 只保留必要的文件和依赖
- **高可靠调用**: 后端使用异步 `httpx` 调用硅基流动 API，支持流式响应并强化错误处理

## 🆕 最新功能 (2025-09-30)

### 🔐 用户认证系统
- **JWT Token 认证**: 安全的用户身份验证
- **注册登录功能**: 支持用户注册、登录、登出
- **滑动验证码**: 防止暴力破解，提升安全性
- **用户信息管理**: 支持修改昵称和密码
- **动态背景登录页**: 流动渐变效果，现代化设计
- **路由守卫**: 未登录自动跳转登录页
- **欢迎信息展示**: 导航栏显示用户昵称

### ✨ AI图片编辑
- 集成 Qwen-Image-Edit-2509 模型，支持基于自然语言指令的智能图片编辑
  - 背景更换、物体添加/移除
  - 颜色调整、风格转换
  - 迭代编辑、原图对比
  - 快速指令模板

### 🎨 界面优化
- 统一采用左右布局设计，提升用户体验
- 优化未登录状态的API调用逻辑

### 🔧 后端优化
- 使用 `httpx.AsyncClient` 提升性能和可靠性
- 安全日志：鉴权头脱敏与错误详情提取，保护API密钥安全

## 🗂️ 项目结构

```
ai-service/
│
├── app/                        # 应用主目录
│   ├── api/                   # API接口
│   │   ├── ai_endpoints.py   # AI服务端点
│   │   ├── auth_endpoints.py # 认证端点 🆕
│   │   └── __init__.py
│   │
│   ├── core/                  # 核心配置
│   │   ├── config.py         # 应用配置
│   │   ├── logger.py         # 日志配置
│   │   ├── auth.py           # JWT认证逻辑 🆕
│   │   ├── user_manager.py   # 用户管理 🆕
│   │   ├── siliconflow_models.py  # 模型配置
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
│   │   │   ├── Login.vue           # 登录页面 🆕
│   │   │   ├── TextAnalysis.vue    # 文本分析
│   │   │   ├── CodeAssist.vue      # 代码助手
│   │   │   ├── Chat.vue            # 智能对话
│   │   │   ├── OCR.vue             # 文字识别
│   │   │   ├── ImageDescription.vue # 图像描述
│   │   │   └── ImageEdit.vue       # 图片编辑
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
├── static/                    # 前端构建输出（自动生成）
├── data/                      # 数据目录
│   └── users.json            # 用户数据 🆕
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

# 默认模型配置
DEFAULT_MODEL=zai-org/GLM-4.5
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=2000

# 认证配置 🆕
{{ ... }}
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
- 🔐 **登录页面**: http://localhost:8000/login （首次访问会自动跳转）
- 📚 **API文档**: http://localhost:8000/docs （可交互测试）
- 📊 **ReDoc文档**: http://localhost:8000/redoc （只读文档）

**开发模式:**
- 🎨 **前端开发**: http://localhost:3000 （热重载，自动打开浏览器）
- 🔌 **后端API**: http://localhost:8000

**默认账号:**
- 👤 用户名: `admin`
- 🔑 密码: `123456` （首次启动自动创建）

## 📚 API接口

### 🔐 认证接口

#### 用户注册
```python
POST /api/v1/auth/register
{
    "username": "testuser",
    "nickname": "测试用户（可选）",
    "password": "password123",
    "confirm_password": "password123"
}
```

#### 用户登录
```python
POST /api/v1/auth/login
{
    "username": "admin",
    "password": "123456"
}

# 响应
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1440,
    "nickname": "管理员"
}
```

#### 更新用户信息
```python
PUT /api/v1/auth/profile
Authorization: Bearer <token>
{
    "nickname": "新昵称（可选）",
    "old_password": "旧密码（修改密码时必填）",
    "new_password": "新密码（可选）"
}
```

#### 获取当前用户信息
```python
GET /api/v1/auth/me
Authorization: Bearer <token>
```

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

### 8. 图片编辑 ✨ (新增)
```python
POST /api/v1/ai/image/edit
FormData:
- file: 图片文件
- instruction: 编辑指令（自然语言描述）

# 示例指令：
# - "将背景改成海滩"
# - "去掉图片中的文字"
# - "改成黑白照片"
# - "添加日落效果"
```

### 9. 获取模型列表
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
- **zai-org/GLM-4.5**: 智谱AI对话模型（默认，免费）
- **moonshotai/Kimi-K2-Instruct-0905**: Moonshot AI文本对话模型（免费）

### 视觉模型
- **zai-org/GLM-4.5V**: 智谱AI视觉语言模型，用于OCR识别（免费）

### 图片编辑模型 ✨
- **Qwen/Qwen-Image-Edit-2509**: 通义千问图片编辑模型（免费）
  - 支持背景更换、物体添加/移除
  - 支持颜色调整、风格转换
  - 基于自然语言指令的智能编辑

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

# 图片编辑 ✨
curl -X POST http://localhost:8000/api/v1/ai/image/edit \
  -F "file=@image.jpg" \
  -F "instruction=将背景改成海滩"

# 获取模型列表
curl http://localhost:8000/api/v1/ai/models
```

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

## 🐳 Docker 部署

### 开发环境部署

适用于本地开发和测试：

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入真实的 API 密钥

# 2. 启动服务
docker compose up -d

# 3. 查看服务状态
docker compose ps

# 4. 查看日志
docker compose logs -f
```

访问地址：
- 🎨 前端界面: http://localhost:8080
- 🔌 后端API: http://localhost:8000

### 生产环境部署（云服务器）

适用于 CentOS 7.9 等 Linux 服务器：

#### 快速部署

```bash
# 1. 赋予部署脚本执行权限
chmod +x deploy.sh

# 2. 执行部署
./deploy.sh deploy
```

#### 手动部署

```bash
# 1. 配置环境变量
cp .env.production .env
vim .env  # 填入真实配置

# 2. 创建必要目录
mkdir -p data logs temp_uploads

# 3. 构建并启动服务
docker compose -f docker-compose.prod.yml up -d

# 4. 配置宿主机 nginx 反向代理
sudo cp nginx-host.conf /etc/nginx/conf.d/pure-ai-service.conf
sudo vim /etc/nginx/conf.d/pure-ai-service.conf  # 修改域名
sudo nginx -t
sudo systemctl reload nginx
```

#### 常用运维命令

```bash
# 查看服务状态
./deploy.sh status

# 查看日志
./deploy.sh logs
./deploy.sh logs backend  # 只看后端日志

# 重启服务
./deploy.sh restart

# 更新服务
./deploy.sh update

# 备份数据
./deploy.sh backup

# 停止服务
./deploy.sh stop
```

### Docker 部署说明

详细的部署文档请参考：
- 📖 [完整部署指南](DEPLOYMENT.md) - 包含环境要求、部署步骤、故障排查等
- 🔧 [部署脚本说明](deploy.sh) - 自动化部署工具
- 🌐 [Nginx 配置示例](nginx-host.conf) - 反向代理配置

**配置文件说明：**
- `Dockerfile` - 后端镜像构建文件
- `docker-compose.yml` - 开发环境编排配置
- `docker-compose.prod.yml` - 生产环境编排配置
- `frontend/Dockerfile` - 前端镜像构建文件
- `frontend/nginx.conf` - 前端容器内 nginx 配置

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📞 联系方式

如有问题，请提交Issue或联系维护者。