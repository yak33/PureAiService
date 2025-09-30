# 🎨 Qwen-Image-Edit-2509 图片编辑功能集成文档

## 📋 概述

成功集成了硅基流动平台的 **Qwen/Qwen-Image-Edit-2509** 图片编辑模型，实现了基于自然语言指令的 AI 图片编辑功能。

## ✨ 功能特性

- 🖼️ **智能图片编辑**: 通过自然语言描述实现图片修改
- 🎯 **多种编辑类型**: 支持背景更换、物体添加/移除、颜色调整、风格转换等
- 🔄 **迭代编辑**: 可以将编辑结果作为新的源图片继续编辑
- 👁️ **对比查看**: 提供原图与编辑后图片的对比功能
- 📥 **结果下载**: 支持下载编辑后的图片
- 🚀 **快速模板**: 提供常用编辑指令模板

## 🛠️ 技术实现

### 1. 后端实现

#### 模型配置 (`app/core/siliconflow_models.py`)
```python
"image_edit": {
    "Qwen/Qwen-Image-Edit-2509": {
        "name": "Qwen/Qwen-Image-Edit-2509",
        "description": "通义千问图片编辑模型，支持基于自然语言指令的图片编辑",
        "max_tokens": 2048,
        "input_price": 0,
        "output_price": 0
    }
}
```

#### 服务方法 (`app/services/pure_ai_service.py`)
- `edit_image()`: 图片编辑核心方法
  - 接收 base64 编码的图片和编辑指令
  - 调用硅基流动 `/v1/images/generations` API
  - 下载生成的图片并转换为 base64
  - 返回编辑后的图片数据

**重要**: 图片编辑使用的是 `/v1/images/generations` 接口，而不是 `/v1/chat/completions` 接口。

请求参数：
```python
{
    "model": "Qwen/Qwen-Image-Edit-2509",
    "prompt": "编辑指令",
    "image": "data:image/jpeg;base64,<base64_data>",
    "num_inference_steps": 20,
    "guidance_scale": 7.5,
    "batch_size": 1
}
```

响应格式：
```python
{
    "images": [{"url": "https://..."}],
    "timings": {"inference": 1234},
    "seed": 123456
}
```

#### API 端点 (`app/api/ai_endpoints.py`)
- `POST /api/v1/ai/image/edit`: 图片编辑接口
  - 参数: `file` (图片文件), `instruction` (编辑指令)
  - 返回: 编辑后的图片 (base64)
  - 响应包含: `edited_image`, `seed`, `timings`, `image_url`

### 2. 前端实现

#### API 服务 (`frontend/src/services/api.js`)
```javascript
editImage: (formData) => api.post('/ai/image/edit', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})
```

#### 页面组件 (`frontend/src/views/ImageEdit.vue`)
功能包括：
- 图片上传和预览
- 编辑指令输入
- 快速指令模板
- 编辑结果展示
- 图片对比查看
- 结果下载
- 迭代编辑

#### 路由配置 (`frontend/src/main.js`)
```javascript
{ path: '/image-edit', component: ImageEdit }
```

#### 导航菜单 (`frontend/src/App.vue`)
添加了"图片编辑"菜单项

## 📝 使用说明

### 1. 上传图片
- 支持 JPG、PNG、WebP 格式
- 文件大小限制: 10MB
- 可通过拖拽或点击上传

### 2. 输入编辑指令
编辑指令示例：
- 把背景改成海滩
- 给人物添加一顶帽子
- 将天空变成日落效果
- 去掉图片中的文字
- 改成黑白照片
- 添加雪花效果

### 3. 查看结果
- 实时预览编辑后的图片
- 可以下载编辑结果
- 支持原图与编辑后图片对比查看
- 可将编辑后的图片作为新源图继续编辑

## 💡 使用技巧

### 编写有效的编辑指令
1. **清晰具体**: 使用明确的描述词
   - ✅ 好: "将背景改成日落时的海滩"
   - ❌ 差: "改一下背景"

2. **专注单一修改**: 一次只修改一个主要方面
   - ✅ 好: "添加一顶红色的帽子"
   - ❌ 差: "添加帽子并改变背景还要调整颜色"

3. **描述期望结果**: 而不是修改过程
   - ✅ 好: "让图片看起来像素描风格"
   - ❌ 差: "用算法转换成素描"

4. **指定风格和氛围**: 可以增强效果
   - "改成温暖的秋天氛围"
   - "转换为赛博朋克风格"

### 最佳实践
- 使用高质量的源图片
- 避免过于复杂的指令
- 可以多次迭代优化
- 及时保存满意的结果

## 🎯 支持的编辑类型

1. **背景修改**
   - 更换场景背景
   - 去除背景
   - 添加背景元素

2. **物体操作**
   - 添加新物体
   - 移除现有物体
   - 修改物体特征

3. **颜色和光线**
   - 调整色调
   - 改变光线效果
   - 应用滤镜

4. **风格转换**
   - 艺术风格转换
   - 黑白/彩色转换
   - 特殊效果添加

## 🔧 配置要求

### 环境变量
确保在 `.env` 文件中配置了硅基流动 API 密钥：
```
OPENAI_API_KEY=your_siliconflow_api_key
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
```

### 依赖包
- 后端: FastAPI, httpx, python-multipart
- 前端: Vue 3, Ant Design Vue

## 📊 模型信息

- **模型名称**: Qwen/Qwen-Image-Edit-2509
- **提供商**: 阿里巴巴通义千问
- **平台**: 硅基流动 (SiliconFlow)
- **定价**: 免费
- **能力**: 图片编辑、风格转换、物体操作
- **API 接口**: `/v1/images/generations` (图片生成接口)
- **图片 URL 有效期**: 1小时（需要及时下载并转换为 base64）

## ⚠️ 重要提示

1. **正确的 API 接口**: Qwen-Image-Edit-2509 使用 `/v1/images/generations` 接口，**不是** `/v1/chat/completions` 接口
2. **图片 URL 有效期**: API 返回的图片 URL 仅有效 1 小时
3. **请求参数**: 必须包含 `model`, `prompt`, `image` 字段
4. **响应格式**: 返回包含图片 URL、随机种子和处理时间的 JSON 对象
5. **图片显示策略**: 
   - 优先使用 API 返回的直接 URL（浏览器可以直接访问显示）
   - 后端尝试下载并转换为 base64 作为备用（可能因权限问题失败）
   - 前端优先使用 URL，确保图片能够正常显示

## 🚀 快速开始

1. 启动后端服务
```bash
python start.py
```

2. 启动前端开发服务器
```bash
cd frontend
npm run dev
```

3. 访问应用
- 打开浏览器访问 `http://localhost:5173`
- 点击导航栏的"图片编辑"
- 上传图片并输入编辑指令
- 查看和下载编辑结果

## 📚 相关文档

- [硅基流动官方文档](https://docs.siliconflow.cn/docs)
- [Qwen-Image-Edit-2509 模型介绍](https://docs.siliconflow.cn/docs)

## 🎉 功能亮点

- ✅ 完全集成到现有 AI 服务平台
- ✅ 统一的 API 设计风格
- ✅ 美观的用户界面
- ✅ 完善的错误处理
- ✅ 支持迭代编辑工作流
- ✅ 提供使用指南和示例

## 作者

ZHANGCHAO

---

**注意**: 此功能依赖硅基流动平台的 Qwen-Image-Edit-2509 模型，请确保 API 密钥有效且有足够的配额。
