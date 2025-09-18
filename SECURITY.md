# 安全配置指南

## 重要提醒

**绝对不要**将包含真实 API 密钥或其他敏感信息的 `.env` 文件提交到 Git 仓库！

## 配置步骤

1. **复制示例配置文件**
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**
   在 `.env` 文件中填入您的真实 API 密钥：
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **验证 .gitignore**
   确保 `.gitignore` 文件包含以下内容：
   ```
   .env
   .env.local
   .env.production
   ```

## 安全最佳实践

### ✅ 应该做的
- 使用环境变量存储敏感信息
- 为不同环境（开发、测试、生产）使用不同的配置文件
- 定期轮换 API 密钥
- 使用密钥管理服务（如 AWS Secrets Manager、Azure Key Vault）

### ❌ 不应该做的
- 永远不要在代码中硬编码密钥
- 不要在公开仓库中提交 `.env` 文件
- 不要在日志中打印敏感信息
- 不要通过不安全的渠道（如邮件、即时通讯）分享密钥

## 如果密钥泄露了怎么办？

1. **立即撤销**泄露的密钥
2. **生成新密钥**并更新配置
3. **检查日志**查看是否有未授权的使用
4. **审查代码历史**确保敏感信息已从所有提交中移除

## 从 Git 历史中移除敏感信息

如果您已经不小心提交了敏感信息，可以使用以下命令清理：

```bash
# 使用 BFG Repo-Cleaner（推荐）
bfg --delete-files .env

# 或使用 git filter-branch
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all
```

注意：清理后需要强制推送，这会改变仓库历史！