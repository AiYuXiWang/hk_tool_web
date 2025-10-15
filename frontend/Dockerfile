# 多阶段构建Dockerfile - UI优化版本
# Stage 1: 构建阶段
FROM node:18-alpine AS builder

# 设置工作目录
WORKDIR /app

# 复制package文件
COPY package*.json ./
COPY package-lock.json ./

# 安装依赖
RUN npm ci --only=production && npm cache clean --force

# 复制源代码
COPY . .

# 构建应用
ARG NODE_ENV=production
ARG BUILD_ENV=production
ENV NODE_ENV=${NODE_ENV}
ENV BUILD_ENV=${BUILD_ENV}

# 生成构建信息
RUN echo "BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" > build-info.json && \
    echo "GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" >> build-info.json && \
    echo "NODE_ENV=${NODE_ENV}" >> build-info.json

# 构建应用
RUN npm run build

# 分析构建包大小（可选）
RUN npx vite-bundle-analyzer dist/ --mode json --output bundle-analysis.json || true

# Stage 2: 生产阶段
FROM nginx:alpine AS production

# 安装必要的工具
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# 创建非root用户
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# 复制自定义nginx配置
COPY nginx.conf /etc/nginx/nginx.conf
COPY mime.types /etc/nginx/mime.types

# 复制构建产物
COPY --from=builder --chown=nextjs:nodejs /app/dist /usr/share/nginx/html

# 复制构建信息
COPY --from=builder /app/build-info.json /usr/share/nginx/html/build-info.json
COPY --from=builder /app/bundle-analysis.json /usr/share/nginx/html/bundle-analysis.json || true

# 创建健康检查脚本
COPY healthcheck.sh /usr/local/bin/healthcheck.sh
RUN chmod +x /usr/local/bin/healthcheck.sh

# 设置正确的权限
RUN chown -R nextjs:nodejs /usr/share/nginx/html && \
    chown -R nextjs:nodejs /var/cache/nginx && \
    chown -R nextjs:nodejs /var/log/nginx && \
    chown -R nextjs:nodejs /etc/nginx/conf.d

# 创建nginx运行时需要的目录
RUN touch /var/run/nginx.pid && \
    chown -R nextjs:nodejs /var/run/nginx.pid

# 切换到非root用户
USER nextjs

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD /usr/local/bin/healthcheck.sh

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]

# Stage 3: 开发环境
FROM node:18-alpine AS development

WORKDIR /app

# 安装开发依赖
COPY package*.json ./
RUN npm ci

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 5173

# 开发环境启动命令
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# Stage 4: 测试环境
FROM node:18-alpine AS testing

WORKDIR /app

# 安装所有依赖（包括开发依赖）
COPY package*.json ./
RUN npm ci

# 复制源代码
COPY . .

# 运行测试
RUN npm run test:coverage

# 构建测试版本
RUN npm run build

# 用于测试的nginx配置
FROM nginx:alpine AS testing-server

COPY --from=testing /app/dist /usr/share/nginx/html
COPY nginx.test.conf /etc/nginx/nginx.conf

EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]