# 贡献指南

感谢你考虑为 AI 服务平台做出贡献！

## 🤝 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 检查 [Issues](https://github.com/yourusername/PureAiService/issues) 确保问题未被报告
2. 创建新的 Issue，清楚地描述：
   - 问题的详细描述
   - 复现步骤
   - 预期行为
   - 实际行为
   - 环境信息（操作系统、Python版本、依赖版本等）

### 提交代码

#### 开发流程

1. **Fork 项目**
   ```bash
   # 在 GitHub 上 Fork 项目
   # 克隆你的 Fork
   git clone https://github.com/your-username/PureAiService.git
   cd PureAiService
   ```

2. **创建分支**
   ```bash
   git checkout -b feature/your-feature-name
   # 或
   git checkout -b fix/your-bug-fix
   ```

3. **设置开发环境**
   
   **后端:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   
   **前端:**
   ```bash
   cd frontend
   pnpm install
   ```

4. **进行修改**
   - 编写清晰的代码和注释
   - 遵循项目的代码风格
   - 添加或更新测试
   - 更新相关文档

5. **测试你的修改**
   
   **后端:**
   ```bash
   pytest
   ```
   
   **前端:**
   ```bash
   cd frontend
   pnpm lint
   ```

6. **提交更改**
   ```bash
   git add .
   git commit -m "✨ feat: 添加新功能描述"
   ```

7. **推送到你的 Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

8. **创建 Pull Request**
   - 在 GitHub 上创建 Pull Request
   - 清楚地描述你的更改
   - 链接相关的 Issue

## 📝 代码规范

### 后端 (Python)

- 遵循 [PEP 8](https://pep8.org/) 代码风格
- 使用类型提示 (Type Hints)
- 函数和类需要有文档字符串
- 变量和函数命名使用 snake_case
- 类命名使用 PascalCase

```python
def process_text(text: str, max_length: int = 100) -> dict:
    """
    处理文本内容
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        处理结果字典
    """
    # 实现代码
    pass
```

### 前端 (Vue/JavaScript)

- 遵循 ESLint 配置
- 使用 Vue 3 Composition API
- 组件命名使用 PascalCase
- 函数和变量使用 camelCase
- 使用 `const` 和 `let`，避免 `var`

```vue
<script setup>
import { ref, computed } from 'vue'

const userName = ref('')
const isValid = computed(() => userName.value.length > 0)

const handleSubmit = () => {
  // 实现代码
}
</script>
```

## 💬 Commit 规范

使用约定式提交 (Conventional Commits)：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

- ✨ `feat`: 新功能
- 🐛 `fix`: Bug 修复
- 📝 `docs`: 文档更新
- 💄 `style`: 代码格式（不影响代码运行）
- ♻️ `refactor`: 重构
- ⚡️ `perf`: 性能优化
- ✅ `test`: 测试相关
- 🔧 `chore`: 构建过程或辅助工具的变动
- ⏪ `revert`: 回退
- 🚀 `deploy`: 部署相关

### 示例

```bash
git commit -m "✨ feat(chat): 添加多轮对话历史记录功能"
git commit -m "🐛 fix(api): 修复图像上传大小限制问题"
git commit -m "📝 docs(readme): 更新安装说明"
```

## 🔍 Pull Request 检查清单

提交 PR 前请确认：

- [ ] 代码遵循项目代码规范
- [ ] 已添加或更新相关测试
- [ ] 所有测试通过
- [ ] 已更新相关文档
- [ ] Commit 信息清晰明确
- [ ] 没有合并冲突
- [ ] 已在本地充分测试

## 🌟 项目结构

```
PureAiService/
├── app/                    # 后端应用
│   ├── api/               # API 路由
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模式
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── frontend/              # 前端应用
│   └── src/
│       ├── views/         # 页面组件
│       ├── components/    # 通用组件
│       ├── services/      # API 封装
│       └── utils/         # 工具函数
├── tests/                 # 测试文件
└── docs/                  # 文档
```

## 📚 开发资源

### 后端
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)

### 前端
- [Vue 3 文档](https://cn.vuejs.org/)
- [Ant Design Vue 文档](https://antdv.com/)
- [Vite 文档](https://cn.vitejs.dev/)

## 🎯 优先级功能

欢迎贡献以下功能：

- [ ] 更多 AI 模型支持
- [ ] 用户权限管理系统
- [ ] 对话历史搜索功能
- [ ] 批量文件处理
- [ ] API 使用统计和限流
- [ ] 多语言国际化支持
- [ ] 移动端适配优化
- [ ] 单元测试覆盖

## ❓ 获取帮助

如果你在贡献过程中遇到问题：

1. 查看项目 [文档](README.md)
2. 搜索现有的 [Issues](https://github.com/yourusername/PureAiService/issues)
3. 创建新的 Issue 询问
4. 联系项目维护者

## 📜 行为准则

请遵循以下原则：

- 尊重所有贡献者
- 接受建设性批评
- 专注于对社区最有利的事情
- 保持友好和包容的态度

## 📄 许可证

通过向本项目贡献代码，你同意你的贡献将在 [MIT License](LICENSE) 下授权。

---

再次感谢你的贡献！🎉
