# AI Daily + DeepSeek 自动化配置指南

## ✅ DeepSeek API 已配置

你的 API Key：`sk-0215bf8b03544c8581d9ed5ffcb66142`

---

## 🚀 部署到阿里云服务器

### 步骤 1：SSH 登录服务器

```bash
ssh root@你的服务器 IP
```

### 步骤 2：安装必要工具

```bash
# 更新系统
apt update && apt upgrade -y

# 安装 Git（如果未安装）
apt install -y git

# 安装 curl
apt install -y curl

# 安装 Python3（如果未安装）
apt install -y python3 python3-pip
```

### 步骤 3：克隆项目

```bash
# 创建目录
mkdir -p /var/www/ai-daily
cd /var/www/ai-daily

# 克隆 GitHub 仓库
git clone https://github.com/Kingoe/ai-daily.git .
```

### 步骤 4：配置 Nginx（如果还没配置）

```bash
# 创建 Nginx 配置文件
cat > /etc/nginx/sites-available/ai-daily << 'EOF'
server {
    listen 80;
    server_name ai.kingoecode.com;

    # 日志文件
    access_log /var/log/nginx/ai-daily-access.log;
    error_log /var/log/nginx/ai-daily-error.log;

    # 静态文件根目录
    root /var/www/ai-daily/docs;
    index index.html;

    # 启用 gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json application/javascript;

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 主页面
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/ai-daily /etc/nginx/sites-enabled/ai-daily

# 测试配置
nginx -t

# 重载 Nginx
systemctl reload nginx
```

### 步骤 5：配置自动化脚本

```bash
# 创建脚本目录
mkdir -p /usr/local/bin/ai-daily

# 复制自动化脚本
cp /var/www/ai-daily/scripts/auto-generate-deepseek.sh /usr/local/bin/ai-daily/generate.sh

# 设置执行权限
chmod +x /usr/local/bin/ai-daily/generate.sh

# 创建日志目录
mkdir -p /var/log/ai-daily
chmod 755 /var/log/ai-daily
```

### 步骤 6：测试运行脚本

```bash
# 手动运行一次
/usr/local/bin/ai-daily/generate.sh

# 查看日志
tail -f /var/log/ai-daily/generate.log
```

如果看到 "完成" 字样，说明配置成功！

### 步骤 7：配置 Crontab 定时任务

```bash
# 编辑 crontab
crontab -e
```

添加以下行（每天北京时间 16:00 执行）：

```bash
# AI Daily 自动化生成（使用 DeepSeek，成本 ¥0.03/天）
0 8 * * * /usr/local/bin/ai-daily/generate.sh >> /var/log/ai-daily/cron.log 2>&1
```

保存并退出。

### 步骤 8：验证 Crontab

```bash
# 查看已配置的定时任务
crontab -l

# 重启 cron 服务
systemctl restart cron
```

---

## 🔍 验证配置

### 1. 检查 Nginx 状态

```bash
systemctl status nginx
```

应该显示 `active (running)`。

### 2. 检查 DNS 解析

在本地电脑执行：

```bash
ping ai.kingoecode.com
```

应该解析到你的服务器 IP。

### 3. 访问网站

浏览器访问：http://ai.kingoecode.com

应该能看到 AI Daily 网站。

### 4. 检查定时任务日志

```bash
# 查看 cron 日志
tail -f /var/log/ai-daily/cron.log

# 查看生成日志
tail -f /var/log/ai-daily/generate.log
```

---

## 💰 成本监控

### 查看 DeepSeek 使用量

访问：https://platform.deepseek.com/usage

可以查看：
- 每日调用次数
- Token 消耗量
- 余额剩余

### 预估成本

```
每天生成 1 次
每次约 2,000-5,000 tokens
每天成本：¥0.01-0.03
每月成本：¥0.3-1
```

你的 ¥10 充值够用 **10-30 个月**！

---

## 🆘 故障排查

### 问题 1：脚本执行失败

**检查**：
```bash
# 查看错误日志
cat /var/log/ai-daily/cron.log

# 手动测试
/usr/local/bin/ai-daily/generate.sh
```

**常见原因**：
- Git 未配置：`git config --global user.name "Kingoe"`
- 网络问题：检查服务器能否访问 DeepSeek API
- API Key 错误：检查是否正确配置

### 问题 2：网站无法访问

**检查**：
```bash
# Nginx 状态
systemctl status nginx

# Nginx 错误日志
tail -f /var/log/nginx/ai-daily-error.log

# 检查文件权限
ls -la /var/www/ai-daily/docs
```

### 问题 3：DeepSeek API 调用失败

**测试**：
```bash
curl -X POST "https://api.deepseek.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-0215bf8b03544c8581d9ed5ffcb66142" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"你好"}]}'
```

如果返回错误，检查：
- API Key 是否正确
- 余额是否充足
- 网络是否通畅

---

## 📊 日常运维

### 查看今日是否已生成

```bash
cd /var/www/ai-daily
ls -la docs/data/$(date +%Y-%m-%d).json
```

### 手动触发生成

```bash
/usr/local/bin/ai-daily/generate.sh
```

### 查看历史数据

```bash
cd /var/www/ai-daily/docs/data
ls -lh *.json
```

### 更新代码

```bash
cd /var/www/ai-daily
git pull origin main
```

---

## 🎉 完成！

配置完成后，系统将：

✅ 每天北京时间 16:00 自动采集 AI 新闻  
✅ 使用 DeepSeek 生成摘要（成本 ¥0.03/天）  
✅ 自动提交到 GitHub  
✅ 自动部署到网站  
✅ 每月成本仅 ¥0.5-1  

**完全自动化，无需人工干预！**

---

## 📝 下一步

1. **执行上述部署步骤**（复制粘贴命令到服务器）
2. **配置阿里云 DNS**：添加 `ai` 子域名解析
3. **测试访问**：http://ai.kingoecode.com
4. **等待第一次自动执行**：明天下午 4 点

需要我帮你直接连接服务器并执行部署吗？😊
