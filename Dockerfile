FROM python:3.11-slim
LABEL authors="gouzu"

# 复制项目代码
COPY /QQBotAPI /QQBotAPI
COPY /shared /shared
COPY /src /src
WORKDIR .

# 安装Python依赖
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# 暴露端口
EXPOSE 8000

# 创建并暴露 databases, apps, AppData 目录
RUN mkdir -p /databases /apps /AppData
VOLUME ["/databases", "/apps", "/AppData"]

# 修正入口点
ENTRYPOINT ["python3", "./src/main.py"]