# 使用 Python 3.9 官方镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1


# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ && \
    pip install gunicorn -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目文件
COPY . .

# 创建 cache 目录
RUN mkdir -p cache

# 暴露端口
EXPOSE 8311

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8311/')" || exit 1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:8311", "--threads", "4", "--timeout", "120", "fund_server:app"]
