FROM ubuntu:latest
LABEL authors="gouzu"

# 暴露端口
EXPOSE 8080

# 创建并暴露 databases, apps, AppData 目录
RUN mkdir -p /databases /apps /AppData
VOLUME ["/databases", "/apps", "/AppData"]

ENTRYPOINT ["top", "-b"]