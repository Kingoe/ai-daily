# AI Daily 配置指南

## 🔑 配置 DeepSeek API Key

### 步骤 1：获取 API Key

1. 访问 DeepSeek 平台：https://platform.deepseek.com/
2. 注册/登录账号
3. 进入控制台 → API Keys
4. 创建新的 API Key
5. 复制保存（格式：`sk-xxxxxxxxxxxxxxxx`）

### 步骤 2：本地测试配置

```bash
# 在项目目录执行
export DEEPSEEK_API_KEY="sk-你的 API_Key"

# 验证
echo $DEEPSEEK_API_KEY
```

### 步骤 3：服务器部署配置

```bash
# SSH 登录服务器
ssh root@你的服务器 IP

# 编辑环境变量
nano ~/.bashrc

# 添加到文件末尾
export DEEPSEEK_API_KEY="sk-你的 API_Key"

# 使配置生效
source ~/.bashrc
```

---

## ⚠️ 安全提醒

### ❌ 不要这样做

```bash
# 不要在代码中硬编码 API Key
DEEPSEEK_API_KEY="sk-xxxxx"  # 错误！

# 不要提交包含 API Key 的文件到 Git
git add scripts/*.sh  # 可能包含 Key！
```

### ✅ 应该这样做

```bash
# 使用环境变量
DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"

# 在部署时配置
export DEEPSEEK_API_KEY="sk-xxxxx"

# 或使用 .env 文件（不提交到 Git）
echo "DEEPSEEK_API_KEY=sk-xxxxx" > .env
```

---

## 📝 使用 .env 文件（推荐）

### 创建 .env 文件

```bash
cd /Users/soft/java/ai-code/ai-daily

# 创建 .env 文件
cat > .env << EOF
DEEPSEEK_API_KEY=sk-你的 API_Key
EOF

# 设置权限（只有你能读取）
chmod 600 .env
```

### 在脚本中加载

```bash
# 加载环境变量
source .env

# 运行脚本
python3 scripts/fetch_news.py
```

### .gitignore 配置

确保 `.env` 文件不会被提交到 Git：

```bash
# .gitignore
.env
*.key
*.secret
```

---

## 💰 成本估算

使用 DeepSeek V3：

```
每天生成 1 次
每次约 2,000-5,000 tokens
每天成本：¥0.01-0.03
每月成本：¥0.3-1
```

**充值建议**：¥10 够用 10-20 个月！

---

## 🆘 常见问题

### Q1: API Key 无效？

A: 检查：
- Key 是否正确复制（没有多余空格）
- 是否已充值
- Key 是否已过期

### Q2: 余额不足？

A: 访问 https://platform.deepseek.com/usage 查看使用情况并充值

### Q3: 如何更换 API Key？

A: 
1. 在 DeepSeek 控制台删除旧 Key
2. 创建新 Key
3. 更新环境变量

---

## 🔒 安全最佳实践

1. **永远不要硬编码**：使用环境变量
2. **定期更换**：每 3-6 个月更换一次
3. **限制权限**：只授予必要的权限
4. **监控使用**：定期检查用量和费用
5. **备份 Key**：安全存储，防止丢失

---

**祝你使用愉快！** 🎉
