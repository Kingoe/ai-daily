#!/bin/bash

# AI Daily 服务器部署脚本
# 适用于 Ubuntu 系统

set -e

echo "🚀 开始部署 AI Daily 到服务器..."

# 配置变量
DEPLOY_DIR="/var/www/ai-daily"
NGINX_CONFIG="/etc/nginx/sites-available/ai-daily"
DOMAIN="ai.kingoecode.com"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

echo "✅ 创建部署目录..."
mkdir -p $DEPLOY_DIR

echo "✅ 克隆或更新代码..."
if [ -d "$DEPLOY_DIR/.git" ]; then
    cd $DEPLOY_DIR
    git pull origin main
else
    git clone https://github.com/Kingoe/ai-daily.git $DEPLOY_DIR
fi

echo "✅ 设置文件权限..."
chown -R www-data:www-data $DEPLOY_DIR
chmod -R 755 $DEPLOY_DIR

echo "✅ 创建 Nginx 配置文件..."
cat > $NGINX_CONFIG << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # 日志文件
    access_log /var/log/nginx/ai-daily-access.log;
    error_log /var/log/nginx/ai-daily-error.log;

    # 静态文件根目录
    root $DEPLOY_DIR/docs;
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
        try_files \$uri \$uri/ /index.html;
    }

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
}
EOF

echo "✅ 启用 Nginx 配置..."
ln -sf $NGINX_CONFIG /etc/nginx/sites-enabled/ai-daily

echo "✅ 测试 Nginx 配置..."
nginx -t

echo "✅ 重载 Nginx..."
systemctl reload nginx

echo "✅ 清理 Git 历史（可选）..."
cd $DEPLOY_DIR
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo ""
echo "🎉 部署完成！"
echo ""
echo "📝 下一步操作："
echo "1. 在阿里云 DNS 控制台添加子域名解析："
echo "   主机记录：ai"
echo "   记录类型：A"
echo "   记录值：$(curl -s ifconfig.me || echo '你的服务器 IP')"
echo ""
echo "2. 等待 DNS 生效（通常 1-10 分钟）"
echo ""
echo "3. 访问：http://$DOMAIN"
echo ""
echo "4. （可选）配置 HTTPS："
echo "   sudo certbot --nginx -d $DOMAIN"
echo ""
