# 使用固定补丁版本的 Python 镜像作为基础镜像
FROM python:3.12.13-slim

# 使用 LABEL 替代 MAINTAINER
LABEL maintainer="948080782@qq.com"

# 设置时区
ENV TZ=Asia/Shanghai
# Python 输出强制 UTF-8（与 CI 保持一致，避免容器内 print 中文报错）
ENV PYTHONUTF8=1

# 设置容器内工作目录
WORKDIR /home

# 先复制依赖清单，利用 layer cache 加速依赖安装（仅 requirements 变化时重装）
COPY ./backend/requirements.txt ./requirements.txt

# 安装依赖（使用清华镜像加速）
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制完整 backend 源码 + Alembic 迁移脚本 + 锁文件进镜像（镜像自包含，不再依赖宿主机挂载）
COPY ./backend/ ./

# Alembic 迁移脚本目录由源码自带，无需额外创建

# 暴露端口
EXPOSE 8001

# 运行应用：先校验生产配置，再 upgrade schema，最后启动 uvicorn
# 注意：生产环境必须通过运行时环境变量/机密注入 SECRET_KEY、DOCS_ENABLE=False、DEBUG=False、真实 CORS
CMD ["sh", "-c", "python main.py config-check --env=prod && python main.py upgrade --env=prod && python main.py run --env=prod"]
