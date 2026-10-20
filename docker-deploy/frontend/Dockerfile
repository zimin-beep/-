# 阶段1：构建 Vue 前端
FROM node:20-alpine AS build
WORKDIR /app

COPY package*.json ./
RUN npm install --registry=https://registry.npmmirror.com

COPY . .
RUN npm run build

# 阶段2：Nginx 托管 dist
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# nginx.conf 不打进镜像，由 docker-compose 挂载覆盖，方便改配置不重建镜像
EXPOSE 80
