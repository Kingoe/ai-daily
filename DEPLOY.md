# AI Daily 部署文档

## 📋 部署前准备

### 1. 确认服务器环境

SSH 登录你的阿里云服务器：

```bash
ssh root@你的服务器 IP
```

检查 Nginx 是否已安装：

```bash
nginx -v
```

如果没有安装 Nginx：

```bash
apt update
apt install -y nginx
systemctl enable nginx
systemctl start nginx
```

### 2. 配置阿里云 DNS 解析

登录 [阿里云 DNS 控制台](https://dns.console.aliyun.com/)

添加以下记录：

| 主机记录 | 记录类型 | 记录值 | TTL |
|---------|---------|--------|-----|
| ai | A | 你的服务器 IP | 10 分钟 |

**等待 DNS 生效**（通常 1-10 分钟）

验证 DNS 是否生效：

```bash
ping ai.kingoecode.com
```

应该能看到你的服务器 IP。

---

## 🚀 自动部署（推荐）

### 步骤 1：上传部署脚本

在本地执行：

```bash
# 克隆项目（如果还没有）
git clone https://github.com/Kingoe/ai-daily.git
cd ai-daily

# 推送最新代码
git add .
git commit -m "Add deployment scripts"
git push origin main
```

### 步骤 2：在服务器上运行部署脚本

SSH 登录服务器：

```bash
ssh root@你的服务器 IP
```

下载并执行部署脚本：

```bash
cd /tmp
wget https://raw.githubusercontent.com/Kingoe/ai-daily/main/deploy.sh
chmod +x deploy.sh
sudo ./deploy.sh
```

部署脚本会自动：
- ✅ 克隆项目到 `/var/www/ai-daily`
- ✅ 创建 Nginx 配置
- ✅ 设置文件权限
- ✅ 重载 Nginx

---

## 🔧 手动部署

如果自动脚本失败，可以手动执行：

### 步骤 1：克隆项目

```bash
mkdir -p /var/www/ai-daily
cd /var/www/ai-daily
git clone https://github.com/Kingoe/ai-daily.git .
```

### 步骤 2：创建 Nginx 配置

```bash
nano /etc/nginx/sites-available/ai-daily
```

粘贴以下内容：

```nginx
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
```

保存并退出（Ctrl+X，然后 Y，然后 Enter）。

### 步骤 3：启用配置

```bash
ln -s /etc/nginx/sites-available/ai-daily /etc/nginx/sites-enabled/ai-daily
nginx -t
systemctl reload nginx
```

### 步骤 4：设置权限

```bash
chown -R www-data:www-data /var/www/ai-daily
chmod -R 755 /var/www/ai-daily
```

---

## 🔒 配置 HTTPS（强烈推荐）

使用 Let's Encrypt 免费 SSL 证书：

### 步骤 1：安装 Certbot

```bash
apt install -y certbot python3-certbot-nginx
```

### 步骤 2：获取证书

```bash
certbot --nginx -d ai.kingoecode.com
```

按照提示输入邮箱，同意条款。

Certbot 会自动：
- ✅ 申请 SSL 证书
- ✅ 修改 Nginx 配置启用 HTTPS
- ✅ 配置自动续期

### 步骤 3：验证

访问：https://ai.kingoecode.com

应该能看到安全锁标志。

---

## 📊 与 Open Claw 的共存说明

当前配置：
- **kingoecode.com** → Open Claw（80 端口）
- **ai.kingoecode.com** → AI Daily（80 端口，不同域名）

两者都使用 80 端口，但通过不同的域名区分，Nginx 会根据 `Host` 头自动转发到正确的站点。

**不需要修改 Open Claw 的配置！**

---

## 🔄 更新内容

当你生成了新的 AI 日报数据后：

### 方法 1：自动更新（推荐）

在服务器上执行：

```bash
cd /var/www/ai-daily
git pull origin main
```

### 方法 2：本地推送

在本地项目目录：

```bash
git add .
git commit -m "Update AI daily data for 2026-03-26"
git push origin main
```

然后在服务器上拉取：

```bash
ssh root@你的服务器 IP
cd /var/www/ai-daily
git pull origin main
```

### 方法 3：自动化脚本（高级）

创建定时任务自动更新：

```bash
crontab -e
```

添加：

```bash
# 每天早上 8 点自动更新
0 8 * * * cd /var/www/ai-daily && git pull origin main
```

---

## 🧪 验证部署

### 1. 检查 Nginx 状态

```bash
systemctl status nginx
```

应该显示 `active (running)`。

### 2. 检查配置文件

```bash
nginx -t
```

应该显示 `syntax is ok` 和 `test is successful`。

### 3. 访问网站

浏览器访问：http://ai.kingoecode.com

应该能看到 AI Daily 网站，显示 3 条示例新闻。

### 4. 检查日志

如果有问题，查看日志：

```bash
tail -f /var/log/nginx/ai-daily-error.log
```

---

## 📸 网站架构

```
kingoecode.com
├── / (Open Claw) - 主域名
└── ai. (AI Daily) - 子域名
    ├── / (前端页面)
    └── /data/ (JSON 数据)
```

---

## 🆘 常见问题

### Q1: 访问子域名显示 404

**解决**：
1. 检查 DNS 是否生效：`ping ai.kingoecode.com`
2. 检查 Nginx 配置：`nginx -t`
3. 检查文件权限：`ls -la /var/www/ai-daily/docs`

### Q2: 和 Open Claw 冲突

**解决**：
确保 Nginx 配置文件中 `server_name` 是 `ai.kingoecode.com` 而不是 `kingoecode.com`。

### Q3: HTTPS 证书申请失败

**解决**：
1. 确保 DNS 已经生效
2. 确保 80 端口开放
3. 检查防火墙：`ufw status`

### Q4: 如何删除部署

```bash
# 删除 Nginx 配置
rm /etc/nginx/sites-available/ai-daily
rm /etc/nginx/sites-enabled/ai-daily
systemctl reload nginx

# 删除项目文件
rm -rf /var/www/ai-daily
```

---

## 📞 技术支持

如有问题，请检查：
1. Nginx 日志：`/var/log/nginx/ai-daily-error.log`
2. Git 状态：`cd /var/www/ai-daily && git status`
3. DNS 解析：`nslookup ai.kingoecode.com`

---

**祝你部署顺利！** 🎉
