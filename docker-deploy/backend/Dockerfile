FROM python:3.10-slim

WORKDIR /app

# 系统依赖（OpenCV 运行时需要）
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 保持 pases/yolo1 目录结构，mainyolo1.py 依赖 script_dir 上两级计算 project_root
COPY pases /app/pases

WORKDIR /app/pases/yolo1

EXPOSE 8080

# 生产服务器，比 Flask 自带的多线程稳定
CMD ["waitress-serve", "--host=0.0.0.0", "--port=8080", "--threads=8", "mainyolo1:app"]
