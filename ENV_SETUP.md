# .env 配置说明

## ✅ 已配置

本项目已使用 `.env` 文件管理 API Key，确保敏感信息不被提交到 Git。

## 📝 本地使用

### 1. .env 文件已创建

项目根目录已存在 `.env` 文件，包含 DeepSeek API Key。

### 2. 自动加载

所有脚本会自动加载 `.env` 文件中的 API Key：

```bash
# 直接运行脚本
python3 scripts/fetch_news.py
bash scripts/test-local.sh
```

### 3. 手动配置环境变量（可选）

```bash
export DEEPSEEK_API_KEY="sk-你的 API_Key"
python3 scripts/fetch_news.py
```

## 🚀 服务器部署

### 方式 1：复制 .env 文件

```bash
# 本地复制 .env 到服务器
scp .env root@你的服务器 IP:/var/www/ai-daily/

# SSH 登录验证
ssh root@你的服务器 IP
cd /var/www/ai-daily
ls -la .env  # 应该能看到 .env 文件
```

### 方式 2：在服务器上创建

```bash
# SSH 登录服务器
ssh root@你的服务器 IP

# 创建 .env 文件
cat > /var/www/ai-daily/.env << EOF
DEEPSEEK_API_KEY=sk-你的 API_Key
EOF

# 设置权限（只有 root 能读取）
chmod 600 /var/www/ai-daily/.env
```

### 方式 3：使用环境变量

```bash
# SSH 登录服务器
ssh root@你的服务器 IP

# 编辑 ~/.bashrc
nano ~/.bashrc

# 添加到文件末尾
export DEEPSEEK_API_KEY="sk-你的 API_Key"

# 使配置生效
source ~/.bashrc
```

## 🔒 安全提醒

### ✅ 已做的保护措施

1. `.env` 已添加到 `.gitignore`
2. 脚本使用环境变量而不是硬编码
3. 自动加载本地 `.env` 文件

### ⚠️ 仍需注意

1. **不要手动提交 .env 文件**
   ```bash
   # 错误！不要这样做
   git add .env
   git commit -m "Add API key"
   ```

2. **定期检查 .gitignore**
   ```bash
   cat .gitignore | grep .env
   # 应该看到：.env
   ```

3. **服务器权限设置**
   ```bash
   # 确保只有 root 能读取
   chmod 600 /var/www/ai-daily/.env
   ```

## 📋 文件清单

| 文件 | 包含敏感信息 | 是否提交到 Git | 说明 |
|------|-------------|---------------|------|
| `.env` | ✅ 是 | ❌ 否 | 本地 API Key 配置 |
| `scripts/fetch_news.py` | ❌ 否 | ✅ 是 | 使用环境变量 |
| `scripts/test-local.sh` | ❌ 否 | ✅ 是 | 使用环境变量 |
| `scripts/auto-generate-deepseek.sh` | ❌ 否 | ✅ 是 | 使用环境变量 |
| `CONFIG.md` | ❌ 否 | ✅ 是 | 配置指南（不含实际 Key） |

## 🆘 故障排查

### 问题 1：脚本提示找不到 API Key

**解决**：
```bash
# 检查 .env 文件是否存在
ls -la .env

# 检查内容
cat .env

# 手动加载
source .env
echo $DEEPSEEK_API_KEY
```

### 问题 2：服务器上找不到 .env

**解决**：
```bash
# 检查文件是否存在
ls -la /var/www/ai-daily/.env

# 如果没有，创建它
cat > /var/www/ai-daily/.env << EOF
DEEPSEEK_API_KEY=sk-你的 API_Key
EOF
```

### 问题 3：误提交了 .env 文件

**紧急处理**：
```bash
# 1. 立即撤销提交
git reset HEAD~1

# 2. 从 Git 历史中删除
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# 3. 强制推送
git push --force origin main

# 4. 更换 API Key（重要！）
# 访问 https://platform.deepseek.com/ 删除旧 Key，创建新 Key
```

## 📊 当前配置状态

- ✅ `.env` 文件已创建（本地）
- ✅ `.gitignore` 已配置
- ✅ 脚本已更新使用环境变量
- ✅ python-dotenv 已安装
- ✅ 测试通过

**项目现在可以安全使用了！** 🎉
